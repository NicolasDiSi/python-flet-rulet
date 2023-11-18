import math
from flet import UserControl,FilePicker,icons,ElevatedButton,Text,FilePickerResultEvent,FilePickerFileType,colors,Slider,TextField,Row,Container,Image,transform,Rotate,animation,AnimationCurve,PieChart,alignment,PieChartSection,border,Icon,AlertDialog,Column,TextButton
import json
import os


def is_member(value, iterable):
     for item in iterable:
         if value is item or value == item:
             return True
     return False
 
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
Render a button that opens it's own FilePicker
Adds multiple functionalities such as:
- Be able to switch between save_file and pick_file
- Both modes have a callback argument that triggers on_result
- You can Change the Button being display and its events
- You can change most of the properties of the FilePicker object
'''
class FilePickerExample(UserControl):
    def __init__(self,text="Cargar Archivo",allowed_extensions=['json'],callback=None,icon=None,data = None,file_name = None,save_file=False,**kwargs):
        super().__init__(**kwargs)
        self.selected_files = Text()
        self.callback = callback
        self.icon = icon if icon != None else icons.UPLOAD_FILE if save_file == False else icons.SAVE 
        self.file_picker = FilePicker(self,on_result=self.save_file_result if save_file == True else self.pick_files_result)
        self.file_picker.file_name = file_name
        self.data = data
        self.allowed_extensions = allowed_extensions
        self.button = ElevatedButton(
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
    
    def pick_files_result(self, e: FilePickerResultEvent):
        self.selected_files.value = (
            ", ".join(map(lambda f: f.name, e.files)) if e.files else "Cancelado!"
        )
        if callable(self.callback):
            # print(self.callback)
            self.callback()
            
        self.selected_files.update()
    
    def save_file(self):
        self.file_picker.save_file(
            "Guardar Archivo",
            file_name="wheel.json",
            allowed_extensions=self.allowed_extensions,
            file_type= FilePickerFileType.CUSTOM
        )
        
    def save_file_result(self, e: FilePickerResultEvent):
        if e.path:
            file_name = os.path.basename(e.control.result.path)
            if not file_name.endswith('.json'):
                self.selected_files.bgcolor = colors.RED
                self.selected_files.color = colors.WHITE
                self.selected_files.value = 'Error: The file must have a .json extension'
                self.selected_files.update()
                return
            
            # Check if the file exists
            if not os.path.exists(e.path):
                # If it does not exist, create it
                open(e.path, 'w').close()
            
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
        
    def _before_build_command(self):
        super()._before_build_command()
        
    
    def build(self):
        return Row(
            [
                self.file_picker,
                self.button,
                self.selected_files
            ]
        )
'''
Creates a Slider element with the option for a text field.
'''    
class SliderExample(UserControl):
    def __init__(self,text='%',initial_value=0.1, show_text=True,**kwargs):
        super().__init__(**kwargs)
        self.slider = Slider(value=initial_value, on_change=self.on_change)
        self.text = TextField(value=str(round(initial_value*100)),width=100,on_change=self.on_change,max_length=4) if show_text else None
        self.label = Text(text)
        self.row = Row([self.slider, self.text,self.label] if show_text else [self.slider],spacing=10,run_spacing=10)
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


#This class is used to setup an image as a badge placed on the chart    
class Badge(Container):
    def __init__(self,src:str = None,size:int = None):
        super().__init__(
            content = Image(src) if src != None and os.path.exists(src) else None,
            width = size,
            height = size,
            animate = None,
            animate_rotation = None,
        )
        self.src = src
        
        
    def _before_build_command(self):
        self.content = Image(self.src) if self.src != None and os.path.exists(self.src) else None
        return super()._before_build_command()
       
#Initializes the chart that will represent the Wheel of fortune
class Wheel:
    def __init__(self,radius=200, badge_size=100,center_space_radius=40,data=[]):
        self.data = data
        self.new_data_hash = None
        self.animation_started = False
        
        #Properties
        self.angle = 360
        self.badge_size = badge_size
        self.radius = radius
        self.duration = 10000
        
        self.is_mounted = False
        self.relevant_size = False
        self.container_height = self.radius+center_space_radius
        self.prev_data_hashes = None  # Store hashes of previous data
        self.animate_rotation = animation.Animation(duration=self.duration, curve=AnimationCurve.FAST_LINEAR_TO_SLOW_EASE_IN)
        
        
        #We Declare the chart that will represent the wheel of fortune
        self.chart = PieChart(
            sections=[],
            sections_space=0,
            center_space_radius=center_space_radius,
            rotate=transform.Rotate(0),
            animate_rotation=self.animate_rotation,
            expand=True,
        )
        
        self.container = Container(
            self.chart,
            alignment=alignment.center,
            height=self.container_height*2,
            on_click=self.animate,
        )

        self.sections = []
    
    def set_duration(self,value = None):
        #Update the value of duration if valid
        if value != None:
            self.duration = value
            self.animate_rotation.duration = value
        else:
            #Set the duration equal to the last valid value
            self.animate_rotation.duration = self.duration
        self.chart.animate_rotation = self.animate_rotation
    
    def stop(self):
        self.animate_rotation.duration = 0
        self.chart.rotate.angle = 0
        self.chart.animate_rotation = self.animate_rotation
        self.animation_started = False
        self.chart.update()
        self.set_duration()
        
    @property
    def on_animation_end(self):
        return self.chart.on_animation_end
    #Setter property for the function called on_animation_end
    @on_animation_end.setter
    def on_animation_end(self,value):
        self.chart.on_animation_end = value
    
    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        self._data = value 
    
    def switch_modes(self):
        self.relevant_size = ~self.relevant_size
        
    def calculate_rotation_angles(self,starting_angle, ending_angle, steps):
        # Convertir los ángulos a radianes
        starting_angle_rad = math.radians(starting_angle)
        ending_angle_rad = math.radians(ending_angle)

        # Calcular el ángulo medio
        mid_angle_rad = (starting_angle_rad + ending_angle_rad) / 2

        # Calcular el ángulo de rotación para cada paso
        rotation_angle_per_step = (ending_angle_rad - starting_angle_rad) / steps

        return mid_angle_rad, math.degrees(rotation_angle_per_step)

    def calculate_starting_ending_angles(self,index, steps):
        # Calcular offset cuando lso valores son muy bajos
        initial_rotation = 90
        # Calcular el ángulo de inicio y el ángulo final
        starting_angle = (360 / steps) * index + initial_rotation
        ending_angle = (360 / steps) * (index + 1) + initial_rotation
        return starting_angle, ending_angle
    
    #Creates each section of the PieChart
    def create_section(self, item,index):
        # Crear el badge
        badge = Badge(item["image"], self.badge_size)
        
        if item["image"] != None:
            steps = len(self.data)+1
            #Modificamos la cantidad de pasos que toma el algoritmo en girar la imagen
            if steps <= 4:
                steps -= 1
        
            # Calcular el ángulo de inicio y el ángulo final
            starting_angle, ending_angle = self.calculate_starting_ending_angles(index, steps)
            
            # Calcular el ángulo medio y el ángulo de rotación por paso
            mid_angle, rotation_angle_per_step = self.calculate_rotation_angles(starting_angle, ending_angle, steps)

            
            # Rotar el badge en cada paso
            if index != 0:
                self.angle = mid_angle + math.radians(rotation_angle_per_step * index)
            else:
                # Calcular el ángulo de rotación para el paso actual
                self.angle = mid_angle
                
            # Rotar el badge
            badge.rotate = Rotate(self.angle, alignment.center)
       
        color = item["color"]
        size = 1 if not self.relevant_size else item["probability"]
        
        return PieChartSection(
            size,
            title=item["title"],
            color=color,
            radius=self.radius,
            badge=badge,
            badge_position=0.8,
        )
        
    def create_sections(self):
        # Remove sections that are no longer needed
        self.chart.sections = [section for index, section in enumerate(self.chart.sections) if index in self.data]

        # Create new sections or update existing ones
        for index, item in enumerate(self.data):
            section = self.create_section(item,index)
            if index < len(self.chart.sections) and self.new_data_hash[index] != self.prev_data_hashes[index]:
                print('updating')
                self.chart.sections[index] = section
            else:
                self.chart.sections.append(section)
                
    def update_sections(self,force=False):
        
        # Convert data to hashable form
        self.new_data_hash = [hash(tuple(item.values())) for item in self.data]

        # Only update the sections if the data has changed
        if self.new_data_hash != self.prev_data_hashes or force == True:
            # Update the sections
            self.sections = self.create_sections()
            
            if self.is_mounted:
                self.chart.update()
                self.container.update()

            # Store the current data hashes for the next update
            self.prev_data_hashes = self.new_data_hash
        
    
    #Helper function to transform color values returns a tuple of RGB values
    def hex_to_rgb(self, hex:str):
        hex_value = hex.lstrip('#')
        return tuple(int(hex_value[i:i+2], 16) for i in (0, 2, 4))
    
    #This changes the angle property of the container, we take advantage of Flet dynamic updates
    def animate(self, e):
        self.chart.rotate.angle += 180
        self.chart.update()
        self.animation_started = True
        
        
class KeyBoardKey(Container):
    def __init__(self,icon:str = None,text:str = None):
        super().__init__()
        self.content = KeyBoardKeyRow(icon,text)
        self.border = border.all(1, colors.WHITE54)
        self.border_radius = 10
        self.bgcolor = "0x09000000"
        self.padding = 10
        
class KeyBoardKeyRow(Row):
    def __init__(self, icon:str = None,text:str = None):
        super().__init__()
        self.controls.append(Icon(icon)) if icon != None else None
        self.controls.append(Text(text)) if text != None else None
       
#Alert Dialog to display Keyboard shortcuts
class ShortcutsDialog(AlertDialog):
    def __init__(self, title=""):
        super().__init__(
            title=Text(value=title),
            content=Column([
                    Row([
                        KeyBoardKey(text="Ctrl"),
                        Text("+"),
                        KeyBoardKey(text="F"),
                        Text("Full Screen"),
                    ]),
                    Row([
                        KeyBoardKey(text="Esc"),
                        Text("Exit Full Screen"),
                    ]),
                    Row([
                        KeyBoardKey("SPACE_BAR","Space Bar"),
                        Text("Spin / Stop the Wheel"),
                    ]),
                    Row([
                        KeyBoardKey("SUBDIRECTORY_ARROW_LEFT","Enter"),
                        Text("Focus Last Option"),
                    ]),
                    Row([
                        KeyBoardKey("SYNC_ALT","Tab"),
                        Text("Switch Between Routes"),
                    ]),
                ],
                wrap=True,
                spacing=10,
                run_spacing=10
            ),
            actions=[
                TextButton(
                    text="Continuar",
                    on_click=self.close
                )
            ]
        )

    def close(self, e):
        self.open = False
        e.control.page.update()
#Alert Dialog that is shown when winning
class CongratulationsDialog(AlertDialog):
    def __init__(self, title="", image=None):
        super().__init__(
            title=Text(value=title),
            content=image if image is not None else None,
            actions=[
                TextButton(
                    text="Continuar",
                    on_click=self.close
                )
            ]
        )

    def close(self, e):
        self.open = False
        e.control.page.update()

class InputField(TextField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.focused = False
        
    def on_focus(self,e):
        self.focused = True
        return super().on_focus
    
    def on_blur(self,e):
        self.focused = False
        return super().on_blur
    
    def on_change(self):
        self.focus()
        return super().on_change