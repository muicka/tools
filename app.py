import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
from PIL import Image, ImageTk
import math

class CocoAnnotationTool:
    def __init__(self, root):
        self.root = root
        self.root.title("COCO Annotation Tool pour YOLO Pose")
        self.root.geometry("1200x800")
        
        # Variables de l'application
        self.dataset_path = ""
        self.json_data = None
        self.current_image_index = 0
        self.circles = []
        self.keypoints = []
        self.circle_radius = 5
        self.zoom_factor = 1.0
        self.pan_x = 0
        self.pan_y = 0
        self.drag_data = {"x": 0, "y": 0, "item": None}
        self.mode = "edit"  # "edit" ou "grab"
        self.keypoint_names = []  # Pour stocker les noms des keypoints
        self.image_width = 0
        self.image_height = 0
        
        self.setup_ui()
    
    def setup_ui(self):
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Panneau de contrôle (gauche)
        control_frame = ttk.Frame(main_frame, width=200, padding=10)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        # Frame d'image (droite)
        self.image_frame = ttk.Frame(main_frame)
        self.image_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Canvas pour l'image
        self.canvas = tk.Canvas(self.image_frame, bg="gray")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Événements du canvas
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        # Événements de la molette pour Ubuntu
        self.canvas.bind("<Button-4>", self.on_mouse_wheel_up)    # Pour Linux (scroll up)
        self.canvas.bind("<Button-5>", self.on_mouse_wheel_down)  # Pour Linux (scroll down)
        
        # Bouton pour charger un dataset
        ttk.Button(control_frame, text="Charger Dataset", command=self.load_dataset).pack(fill=tk.X, pady=5)
        
        # Séparateur
        ttk.Separator(control_frame, orient='horizontal').pack(fill=tk.X, pady=10)
        
        # Contrôle de navigation
        nav_frame = ttk.Frame(control_frame)
        nav_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(nav_frame, text="Précédent", command=self.previous_image).pack(side=tk.LEFT, padx=2)
        ttk.Button(nav_frame, text="Suivant", command=self.next_image).pack(side=tk.RIGHT, padx=2)
        
        # Informations sur l'image actuelle
        self.image_info_label = ttk.Label(control_frame, text="Image: 0/0")
        self.image_info_label.pack(fill=tk.X, pady=5)
        
        # Affichage du nom du fichier actuel
        self.filename_label = ttk.Label(control_frame, text="Fichier: ", wraplength=180)
        self.filename_label.pack(fill=tk.X, pady=5)
        
        # Séparateur
        ttk.Separator(control_frame, orient='horizontal').pack(fill=tk.X, pady=10)
        
        # Contrôle du rayon des cercles
        ttk.Label(control_frame, text="Taille des points:").pack(anchor=tk.W)
        self.radius_scale = ttk.Scale(control_frame, from_=1, to=20, orient=tk.HORIZONTAL, 
                                     value=self.circle_radius, command=self.update_circle_radius)
        self.radius_scale.pack(fill=tk.X, pady=5)
        
        # Séparateur
        ttk.Separator(control_frame, orient='horizontal').pack(fill=tk.X, pady=10)
        
        # Contrôles de zoom et déplacement
        ttk.Label(control_frame, text="Mode:").pack(anchor=tk.W)
        self.mode_var = tk.StringVar(value="edit")
        ttk.Radiobutton(control_frame, text="Éditer points", variable=self.mode_var, 
                       value="edit", command=self.change_mode).pack(anchor=tk.W)
        ttk.Radiobutton(control_frame, text="Déplacer image", variable=self.mode_var, 
                       value="grab", command=self.change_mode).pack(anchor=tk.W)
        
        zoom_frame = ttk.Frame(control_frame)
        zoom_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(zoom_frame, text="Zoom +", command=lambda: self.zoom(1.2)).pack(side=tk.LEFT, padx=2)
        ttk.Button(zoom_frame, text="Zoom -", command=lambda: self.zoom(0.8)).pack(side=tk.RIGHT, padx=2)
        ttk.Button(control_frame, text="Reset Vue", command=self.reset_view).pack(fill=tk.X, pady=5)
        
        # Séparateur
        ttk.Separator(control_frame, orient='horizontal').pack(fill=tk.X, pady=10)
        
        # Étiquette pour afficher le nom du keypoint sélectionné
        self.keypoint_label = ttk.Label(control_frame, text="Keypoint: -")
        self.keypoint_label.pack(fill=tk.X, pady=5)
        
        # Étiquette pour afficher les coordonnées du point sélectionné
        self.coord_frame = ttk.Frame(control_frame)
        self.coord_frame.pack(fill=tk.X, pady=5)
        ttk.Label(self.coord_frame, text="Coordonnées:").pack(anchor=tk.W)
        
        coord_details_frame = ttk.Frame(self.coord_frame)
        coord_details_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(coord_details_frame, text="X:").grid(row=0, column=0, sticky=tk.W, padx=2)
        self.x_coord_label = ttk.Label(coord_details_frame, text="-")
        self.x_coord_label.grid(row=0, column=1, sticky=tk.W, padx=2)
        
        ttk.Label(coord_details_frame, text="Y:").grid(row=1, column=0, sticky=tk.W, padx=2)
        self.y_coord_label = ttk.Label(coord_details_frame, text="-")
        self.y_coord_label.grid(row=1, column=1, sticky=tk.W, padx=2)
        
        # Visibilité du point
        visibility_frame = ttk.Frame(self.coord_frame)
        visibility_frame.pack(fill=tk.X, pady=2)
        ttk.Label(visibility_frame, text="Visibilité:").pack(side=tk.LEFT, padx=2)
        self.visibility_label = ttk.Label(visibility_frame, text="-")
        self.visibility_label.pack(side=tk.LEFT, padx=2)
        
        # Séparateur
        ttk.Separator(control_frame, orient='horizontal').pack(fill=tk.X, pady=10)
        
        # Bouton de sauvegarde
        ttk.Button(control_frame, text="Sauvegarder", command=self.save_annotations).pack(fill=tk.X, pady=5)
    
    def load_dataset(self):
        """Charge un dataset COCO"""
        self.dataset_path = filedialog.askdirectory(title="Sélectionner le dossier du dataset")
        if not self.dataset_path:
            return
            
        # Trouver le fichier JSON d'annotations
        json_files = [f for f in os.listdir(self.dataset_path) if f.endswith('.json') and 'annotations' in f.lower()]
        
        if not json_files:
            messagebox.showerror("Erreur", "Aucun fichier JSON d'annotations trouvé dans le dossier.")
            return
            
        # Charger le fichier JSON
        try:
            with open(os.path.join(self.dataset_path, json_files[0]), 'r') as f:
                self.json_data = json.load(f)
                
            # Vérifier la structure du JSON
            if 'images' not in self.json_data or 'annotations' not in self.json_data:
                messagebox.showerror("Erreur", "Format JSON COCO invalide.")
                return
                
            # Récupérer les noms des keypoints si disponibles
            for category in self.json_data.get('categories', []):
                if 'keypoints' in category:
                    self.keypoint_names = category['keypoints']
                    break
                    
            # Initialiser à la première image
            self.current_image_index = 0
            self.update_image_info()
            self.load_current_image()
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de charger le fichier JSON: {str(e)}")
    
    def update_image_info(self):
        """Met à jour l'affichage des informations sur l'image courante"""
        if self.json_data:
            total_images = len(self.json_data['images'])
            self.image_info_label.config(text=f"Image: {self.current_image_index + 1}/{total_images}")
            
            # Mettre à jour le nom du fichier
            if self.current_image_index < len(self.json_data['images']):
                filename = self.json_data['images'][self.current_image_index].get('file_name', '')
                self.filename_label.config(text=f"Fichier: {filename}")
        else:
            self.image_info_label.config(text="Image: 0/0")
            self.filename_label.config(text="Fichier: ")
    
    def load_current_image(self):
        """Charge l'image courante et ses keypoints"""
        if not self.json_data:
            return
            
        # Vérifier les limites de l'index
        if self.current_image_index < 0:
            self.current_image_index = 0
        elif self.current_image_index >= len(self.json_data['images']):
            self.current_image_index = len(self.json_data['images']) - 1
            
        # Récupérer les informations de l'image
        image_info = self.json_data['images'][self.current_image_index]
        image_id = image_info['id']
        image_filename = image_info.get('file_name') or image_info.get('filename')
        
        # Mettre à jour la taille de l'image
        self.image_width = image_info.get('width', 0)
        self.image_height = image_info.get('height', 0)
        
        if not image_filename:
            messagebox.showerror("Erreur", f"Nom de fichier non trouvé pour l'image {self.current_image_index}")
            return
            
        # Charger l'image
        try:
            image_path = os.path.join(self.dataset_path, image_filename)
            self.original_image = Image.open(image_path)
            
            # Si les dimensions ne sont pas dans le JSON, les récupérer de l'image
            if self.image_width == 0 or self.image_height == 0:
                self.image_width, self.image_height = self.original_image.size
                
            self.reset_view(update_image=False)
            self.update_display()
            
            # Charger les keypoints
            self.load_keypoints(image_id)
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de charger l'image: {str(e)}")
    
    def load_keypoints(self, image_id):
        """Charge les keypoints pour l'image courante"""
        self.clear_circles()
        self.keypoints = []
        
        # Réinitialiser l'affichage des coordonnées
        self.clear_keypoint_info()
        
        # Trouver l'annotation correspondant à l'image courante
        for annotation in self.json_data['annotations']:
            if annotation.get('image_id') == image_id and 'keypoints' in annotation:
                keypoints_data = annotation['keypoints']
                
                # Les keypoints COCO sont stockés au format [x1, y1, v1, x2, y2, v2, ...]
                # où v est un flag de visibilité (0: non marqué, 1: marqué mais non visible, 2: visible)
                for i in range(0, len(keypoints_data), 3):
                    if i + 1 < len(keypoints_data):  # Vérifier qu'il y a au moins x et y
                        x, y = keypoints_data[i], keypoints_data[i + 1]
                        visibility = keypoints_data[i + 2] if i + 2 < len(keypoints_data) else 2
                        
                        # Stocker les coordonnées originales (non transformées)
                        self.keypoints.append((x, y, visibility, i // 3))
                
                # Dessiner les cercles pour les keypoints
                self.draw_circles()
                break
    
    def draw_circles(self):
        """Dessine les cercles pour les keypoints"""
        self.clear_circles()
        
        for x, y, visibility, idx in self.keypoints:
            # Vérifier que le point est dans les limites de l'image
            if not (0 <= x <= self.image_width and 0 <= y <= self.image_height):
                # Limiter les coordonnées aux dimensions de l'image
                x = max(0, min(x, self.image_width))
                y = max(0, min(y, self.image_height))
                
                # Mettre à jour les keypoints avec les coordonnées limitées
                for i, (_, _, v, idx_) in enumerate(self.keypoints):
                    if idx_ == idx:
                        self.keypoints[i] = (x, y, v, idx_)
                        break
            
            # Appliquer la transformation (zoom et pan)
            transformed_x, transformed_y = self.transform_point(x, y)
            
            # Couleur basée sur la visibilité (rouge: non visible, vert: visible)
            color = "green" if visibility == 2 else "yellow" if visibility == 1 else "red"
            
            # Dessiner le cercle
            circle = self.canvas.create_oval(
                transformed_x - self.circle_radius, 
                transformed_y - self.circle_radius,
                transformed_x + self.circle_radius, 
                transformed_y + self.circle_radius,
                fill=color, outline="black", tags=f"keypoint_{idx}"
            )
            
            # Ajouter le cercle à la liste
            self.circles.append((circle, idx))
            
            # Ajouter le nom du keypoint au lieu de l'index
            keypoint_name = self.get_keypoint_name(idx)
            self.canvas.create_text(
                transformed_x, transformed_y - self.circle_radius - 5,
                text=keypoint_name, font=("Arial", 8),
                fill="white", tags=f"keypoint_text_{idx}"
            )
    
    def get_keypoint_name(self, idx):
        """Retourne le nom du keypoint à partir de son index"""
        if self.keypoint_names and idx < len(self.keypoint_names):
            return self.keypoint_names[idx]
        else:
            return str(idx)
    
    def clear_circles(self):
        """Supprime tous les cercles du canvas"""
        for circle, _ in self.circles:
            self.canvas.delete(circle)
        self.circles = []
        
        # Supprimer également les textes
        for idx in range(len(self.keypoint_names) if self.keypoint_names else 20):
            self.canvas.delete(f"keypoint_text_{idx}")
    
    def update_display(self):
        """Met à jour l'affichage de l'image avec le zoom et le pan actuels"""
        if not hasattr(self, 'original_image'):
            return
            
        # Redimensionner l'image selon le facteur de zoom
        new_width = int(self.original_image.width * self.zoom_factor)
        new_height = int(self.original_image.height * self.zoom_factor)
        
        # Créer une nouvelle image redimensionnée
        self.display_image = self.original_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        self.photo_image = ImageTk.PhotoImage(self.display_image)
        
        # Mettre à jour le canvas
        self.canvas.delete("image")
        self.canvas.create_image(
            self.pan_x, self.pan_y, 
            anchor=tk.NW, 
            image=self.photo_image, 
            tags="image"
        )
        
        # Mettre à jour la taille du canvas
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))
        
        # Redessiner les cercles
        self.draw_circles()
    
    def transform_point(self, x, y):
        """Transforme les coordonnées d'un point selon le zoom et le pan actuels"""
        return x * self.zoom_factor + self.pan_x, y * self.zoom_factor + self.pan_y
    
    def inverse_transform_point(self, x, y):
        """Transforme des coordonnées canvas en coordonnées image originales"""
        return (x - self.pan_x) / self.zoom_factor, (y - self.pan_y) / self.zoom_factor
    
    def clear_keypoint_info(self):
        """Réinitialise l'affichage des informations du keypoint"""
        self.keypoint_label.config(text="Keypoint: -")
        self.x_coord_label.config(text="-")
        self.y_coord_label.config(text="-")
        self.visibility_label.config(text="-")
    
    def update_keypoint_info(self, idx, x, y, visibility):
        """Met à jour l'affichage des informations du keypoint"""
        # Mettre à jour le nom du keypoint
        keypoint_name = self.get_keypoint_name(idx)
        self.keypoint_label.config(text=f"Keypoint: {keypoint_name}")
            
        # Mettre à jour les coordonnées
        self.x_coord_label.config(text=f"{x:.1f}")
        self.y_coord_label.config(text=f"{y:.1f}")
        
        # Mettre à jour la visibilité
        visibility_text = "Visible" if visibility == 2 else "Non visible" if visibility == 1 else "Non marqué"
        self.visibility_label.config(text=f"{visibility} ({visibility_text})")
    
    def on_mouse_press(self, event):
        """Gère l'événement de clic de souris"""
        if self.mode == "edit":
            # Mode édition: sélectionner et déplacer des points
            closest = self.canvas.find_closest(event.x, event.y)
            if closest and closest[0] != self.canvas.find_withtag("image")[0]:
                # Un point a été sélectionné
                self.drag_data["item"] = closest[0]
                self.drag_data["x"] = event.x
                self.drag_data["y"] = event.y
                
                # Afficher les informations du keypoint sélectionné
                for circle, idx in self.circles:
                    if circle == closest[0]:
                        for kp_x, kp_y, kp_v, kp_idx in self.keypoints:
                            if kp_idx == idx:
                                self.update_keypoint_info(idx, kp_x, kp_y, kp_v)
                                break
                        break
        elif self.mode == "grab":
            # Mode déplacement d'image
            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y
    
    def on_mouse_drag(self, event):
        """Gère l'événement de glisser-déposer"""
        if self.mode == "edit" and self.drag_data["item"]:
            # Déplacer le point sélectionné
            dx = event.x - self.drag_data["x"]
            dy = event.y - self.drag_data["y"]
            
            self.canvas.move(self.drag_data["item"], dx, dy)
            
            # Déplacer également le texte associé si présent
            for _, idx in self.circles:
                if f"keypoint_text_{idx}" in self.canvas.gettags(self.drag_data["item"]) or \
                   f"keypoint_{idx}" in self.canvas.gettags(self.drag_data["item"]):
                    self.canvas.move(f"keypoint_text_{idx}", dx, dy)
                    break
            
            # Mettre à jour les données de glisser-déposer
            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y
            
            # Mettre à jour les coordonnées du keypoint
            for i, (circle, idx) in enumerate(self.circles):
                if circle == self.drag_data["item"]:
                    # Récupérer les nouvelles coordonnées
                    x1, y1, x2, y2 = self.canvas.coords(circle)
                    center_x = (x1 + x2) / 2
                    center_y = (y1 + y2) / 2
                    
                    # Convertir en coordonnées d'image originale
                    orig_x, orig_y = self.inverse_transform_point(center_x, center_y)
                    
                    # Limiter les coordonnées aux dimensions de l'image
                    orig_x = max(0, min(orig_x, self.image_width))
                    orig_y = max(0, min(orig_y, self.image_height))
                    
                    # Mettre à jour les keypoints
                    visibility = self.keypoints[i][2]
                    self.keypoints[i] = (orig_x, orig_y, visibility, idx)
                    
                    # Mettre à jour l'affichage des coordonnées
                    self.update_keypoint_info(idx, orig_x, orig_y, visibility)
                    
                    # Si les coordonnées ont été limitées, mettre à jour la position du cercle
                    new_x, new_y = self.transform_point(orig_x, orig_y)
                    center_x_canvas = (x1 + x2) / 2
                    center_y_canvas = (y1 + y2) / 2
                    
                    if new_x != center_x_canvas or new_y != center_y_canvas:
                        dx_correction = new_x - center_x_canvas
                        dy_correction = new_y - center_y_canvas
                        self.canvas.move(circle, dx_correction, dy_correction)
                        self.canvas.move(f"keypoint_text_{idx}", dx_correction, dy_correction)
                    
                    break
                    
        elif self.mode == "grab":
            # Déplacer l'image
            dx = event.x - self.drag_data["x"]
            dy = event.y - self.drag_data["y"]
            
            self.pan_x += dx
            self.pan_y += dy
            
            # Mettre à jour les données de glisser-déposer
            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y
            
            # Mettre à jour l'affichage
            self.update_display()
    
    def on_mouse_wheel_up(self, event):
        """Gère l'événement de zoom avant (molette vers le haut)"""
        self.zoom(1.1, event.x, event.y)
        
    def on_mouse_wheel_down(self, event):
        """Gère l'événement de zoom arrière (molette vers le bas)"""
        self.zoom(0.9, event.x, event.y)
    
    def zoom(self, factor, x=None, y=None):
        """Ajuste le zoom et met à jour l'affichage"""
        old_zoom = self.zoom_factor
        self.zoom_factor *= factor
        
        # Limiter le facteur de zoom
        self.zoom_factor = max(0.1, min(5.0, self.zoom_factor))
        
        # Si les coordonnées du point de zoom sont fournies, ajuster le pan
        if x is not None and y is not None and old_zoom != self.zoom_factor:
            # Calculer le nouveau pan pour que le point sous la souris reste fixe
            scale_factor = self.zoom_factor / old_zoom
            self.pan_x = x - (x - self.pan_x) * scale_factor
            self.pan_y = y - (y - self.pan_y) * scale_factor
        
        # Mettre à jour l'affichage
        self.update_display()
    
    def reset_view(self, update_image=True):
        """Réinitialise le zoom et le pan"""
        self.zoom_factor = 1.0
        self.pan_x = 0
        self.pan_y = 0
        if update_image:
            self.update_display()
    
    def update_circle_radius(self, value):
        """Met à jour le rayon des cercles"""
        self.circle_radius = float(value)
        self.draw_circles()
    
    def change_mode(self):
        """Change le mode d'interaction (édition ou déplacement)"""
        self.mode = self.mode_var.get()
        
        # Mettre à jour le curseur selon le mode
        if self.mode == "grab":
            self.canvas.config(cursor="fleur")
        else:
            self.canvas.config(cursor="arrow")
    
    def next_image(self):
        """Passe à l'image suivante"""
        if self.json_data and self.current_image_index < len(self.json_data['images']) - 1:
            self.current_image_index += 1
            self.update_image_info()
            self.load_current_image()
    
    def previous_image(self):
        """Passe à l'image précédente"""
        if self.json_data and self.current_image_index > 0:
            self.current_image_index -= 1
            self.update_image_info()
            self.load_current_image()
    
    def save_annotations(self):
        """Sauvegarde les annotations dans le fichier JSON"""
        if not self.json_data:
            messagebox.showwarning("Attention", "Aucun dataset chargé.")
            return
            
        try:
            # Récupérer l'ID de l'image courante
            image_id = self.json_data['images'][self.current_image_index]['id']
            
            # Trouver l'annotation correspondante
            for annotation in self.json_data['annotations']:
                if annotation.get('image_id') == image_id:
                    # Mettre à jour les keypoints
                    keypoints_flat = []
                    for x, y, v, _ in self.keypoints:
                        keypoints_flat.extend([round(x), round(y), int(v)])
                    
                    annotation['keypoints'] = keypoints_flat
                    break
            else:
                messagebox.showwarning("Attention", "Aucune annotation trouvée pour cette image.")
                return
            
            # Sauvegarder le fichier JSON
            json_file = next(f for f in os.listdir(self.dataset_path) 
                            if f.endswith('.json') and 'annotations' in f.lower())
            
            with open(os.path.join(self.dataset_path, json_file), 'w') as f:
                json.dump(self.json_data, f, indent=2)
                
            messagebox.showinfo("Succès", "Annotations sauvegardées avec succès.")
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de sauvegarder les annotations: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = CocoAnnotationTool(root)
    root.mainloop()
