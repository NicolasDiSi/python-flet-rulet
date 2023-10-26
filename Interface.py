import random
import flet as ft
import json
import os

#Normalize the values to handle text inputs throughout the app
def normalize_value(value):
        if isinstance(value, str) and str.isdigit(value):
            value = int(value)
        elif isinstance(value, float) or isinstance(value, int):
            value = round(value)
        else:
            return None

        if value > 100:
            value = 100
        return value

'''
Render a button that opens it's own ft.FilePicker
Adds multiple functionalities such as:
- Be able to switch between save_file and pick_file
- Both modes have a callback argument that triggers on_result
- You can Change the Button being display and its events
- You can change most of the properties of the FilePicker object
'''
class FilePickerExample(ft.UserControl):
    def __init__(self,text="Cargar Archivo",allowed_extensions=['json'],callback=None,icon=None,data = None,file_name = None,save_file=False,**kwargs):
        super().__init__(**kwargs)
        self.selected_files = ft.Text()
        self.callback = callback
        self.icon = icon if icon != None else ft.icons.UPLOAD_FILE if save_file == False else ft.icons.SAVE 
        self.file_picker = ft.FilePicker(self,on_result=self.save_file_result if save_file == True else self.pick_files_result)
        self.file_picker.file_name = file_name
        self.data = data
        self.allowed_extensions = allowed_extensions
        self.button = ft.ElevatedButton(
                   text,
                    icon=self.icon,
                    on_click=lambda _: self.save_file() if save_file == True else self.file_picker.pick_files()  ,
                )
        
    
    def pick_files(self):
        self.file_picker.save_file(
            "Elige el Archivo",
            allowed_extensions=self.allowed_extensions,
            on_result=self.pick_files_result
        )
    
    def pick_files_result(self, e: ft.FilePickerResultEvent):
        self.selected_files.value = (
            ", ".join(map(lambda f: f.name, e.files)) if e.files else "Cancelado!"
        )
        self.selected_files.update()
        if callable(self.callback):
            # print(self.callback)
            self.callback()
    
    def save_file(self):
        self.file_picker.save_file(
            "Guardar Archivo",
            allowed_extensions=self.allowed_extensions,
            file_type= ft.FilePickerFileType.CUSTOM,
        )
        
    def save_file_result(self, e: ft.FilePickerResultEvent):
        
        if e.path:
            file_name = os.path.basename(e.control.result.path)
            if not file_name.endswith('.json'):
                self.selected_files.bgcolor = ft.colors.RED
                self.selected_files.color = ft.colors.WHITE
                self.selected_files.value = 'Error: The file must have a .json extension'
                self.selected_files.update()
                return
            
            with open(e.path, 'w') as f:
                data = self.data
                if callable(self.data):
                    data = self.data()
                
                json.dump(data,f)
                
        self.selected_files.value = "Guardado!"
        self.selected_files.update()
       
        
    @property
    def button(self):
        return self._button

    @button.setter
    def button(self, value):
        self._button = value 
    
    def build(self):
        return ft.Row(
            [
                self.file_picker,
                self.button,
                self.selected_files
            ]
        )
'''
Creates a Slider element with the option for a text field.
'''    
class SliderExample(ft.UserControl):
    def __init__(self,text='%',initial_value=0.1, show_text=True,**kwargs):
        super().__init__(**kwargs)
        self.slider = ft.Slider(value=initial_value, on_change=self.on_change)
        self.text = ft.TextField(value=str(round(initial_value*100)),width=100,on_change=self.on_change,max_length=4) if show_text else None
        self.label = ft.Text(text)
        self.row = ft.Row([self.slider, self.text,self.label] if show_text else [self.slider],spacing=10,run_spacing=10)
        self.min_value = 1
        self.max_value = 100
        self.callback = None

    def on_change(self, e):
        value = self.normalize_value(e.control.value)
        self.set_controls(value)
        
        if callable(self.callback):
            self.callback()
        
        self.text.update()
        self.slider.update()
        e.control.page.update()
        
    #Normalizes string values into valid float values
    def normalize_value(self, value):
        if isinstance(value, str) and str.isdigit(value):
            #value should always less or equal of 1
            value = float(value)
            
            if value > self.max_value:
                value = self.max_value
            if value <= 0:
                value = self.min_value
                
            value = value  / self.max_value
        elif isinstance(value, float) or isinstance(value, int):
            if value <= 0:
                value = 0.01
            value = value % self.max_value
        else:
            return None
            
        return value

    def set_controls(self, value):
        if value is not None:
            self.text.value = str(round(value * self.max_value))
            self.slider.value = value
            # self.slider.update()
            # self.text.update()

    @property
    def string_value(self):
        value = round(self.normalize_value(self.text.value)*self.max_value)
        return value
    
    @property
    def value(self):
        return self.normalize_value(self.text.value)
    
    @value.setter
    def value(self, value):
       new_value = self.normalize_value(value)
       self.set_controls(new_value)
    
    def build(self):
        return self.row
    
#Initializes the chart that will represent the Wheel of fortune
class Wheel:
    def __init__(self,radius=200, badge_size=100,center_space_radius=40,data=[]):
        self.data = data
        
        #Properties
        self.badge_size = badge_size
        self.radius = radius
        self.duration = 10000
        
        self.is_mounted = False
        self.relevant_size = False
        self.container_height = self.radius+center_space_radius
        self.prev_data_hashes = None  # Store hashes of previous data
        self.animate_rotation = ft.animation.Animation(duration=self.duration, curve=ft.AnimationCurve.FAST_LINEAR_TO_SLOW_EASE_IN)
        
        
        #We Declare the chart that will represent the wheel of fortune
        self.chart = ft.PieChart(
            sections=[],
            sections_space=0,
            center_space_radius=center_space_radius,
            expand=True
        )
        
        self.container = ft.Container(
            self.chart,
            rotate=ft.transform.Rotate(0),
            animate_rotation=self.animate_rotation,
            alignment=ft.alignment.center,
            height=self.container_height*2,
            on_click=self.animate
        )
    
        
        self.sections = []
   
    def set_duration(self,value):
        self.animate_rotation.duration = value
        self.container.animate_rotation = self.animate_rotation
    
    @property
    def on_animation_end(self):
        return self.container.on_animation_end
    #Setter property for the function called on_animation_end
    @on_animation_end.setter
    def on_animation_end(self,value):
        self.container.on_animation_end = value
    
    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        self._data = value 
    
    def switch_modes(self):
        self.relevant_size = ~self.relevant_size
        
    def update_sections(self,force=False):
        # Convert data to hashable form
        data_hashes = [hash(tuple(item.values())) for item in self.data]

        # Only update the sections if the data has changed
        if data_hashes != self.prev_data_hashes or force == True:
            # Update the sections
            self.sections = self.create_sections()
            self.chart.sections = self.sections
            
            if self.is_mounted:
                self.chart.update()
                self.container.update()

            # Store the current data hashes for the next update
            self.prev_data_hashes = data_hashes

    def create_sections(self):
        sections = []
        # print(data_hashes)
        for i, item in enumerate(self.data):
            # Create a new section if the previous data doesn't exist
            if self.prev_data_hashes is None or i not in self.prev_data_hashes:
                
                badge = self.create_badge(item["image"], self.badge_size) if item["image"] != None else None
                color = item["color"]
                size = 1 if self.relevant_size == False else item["probability"]
                
                section = ft.PieChartSection(
                    size,
                    title=item["title"],
                    color=color,
                    radius=self.radius,
                    badge=badge,
                    badge_position=0.5,
                )
                sections.append(section)
                
        return sections

    #This method is used to setup an image as a badge placed on the chart    
    def create_badge(self, src, size):
        return ft.Container(
            ft.Image(src),
            width=size,
            height=size,
            animate=None
        )
    #Helper function to transform color values returns a tuple of RGB values
    def hex_to_rgb(self, hex:str):
        hex_value = hex.lstrip('#')
        return tuple(int(hex_value[i:i+2], 16) for i in (0, 2, 4))
    #This changes the angle property of the container, we take advantage of Flet dynamic updates here
    def animate(self, e):
        self.container.rotate.angle += 360
        self.container.update()
        
        
#Alert Dialog that is shown when winning
class CongratulationsDialog(ft.AlertDialog):
    def __init__(self, title="", image=None):
        super().__init__(
            title=ft.Text(value=title),
            content=image if image is not None else None,
            actions=[
                ft.TextButton(
                    text="Continuar",
                    on_click=self.close
                )
            ]
        )

    def close(self, e):
        self.open = False
        e.control.page.update()
        
# class Control:
#     def __init__(self, obj):
#         self.obj = obj
#         self.sliders = {}

#     def add_slider(self, prop_name, unit):
#         slider = SliderExample(unit)
#         slider.max_value = getattr(self.obj, prop_name)
#         self.sliders[prop_name] = slider

#     def update_sliders(self):
#         for prop_name, slider in self.sliders.items():
#             setattr(self.obj, prop_name, slider.value)