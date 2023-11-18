import flet as ft
from flet_contrib.color_picker import ColorPicker
from flet_contrib.color_picker.src.utils import rgb2hex

import time
import random
import json
import os

#Interfaz
from Interface import CongratulationsDialog, FilePickerExample, InputField, ShortcutsDialog, SliderExample, Wheel, normalize_value

def generate_random_color(format):
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    if format == 'hex':
        return rgb2hex((r,g,b))
    else:
        return tuple(r,g,b)

# Prevents Weird EventHandler behavior
img_picker = ft.FilePicker()
class OptionForm(ft.UserControl):
    
    def __init__(self, option_number,parent,**kwargs):
        super().__init__(key= None,**kwargs)
        self.option_number = option_number
        self.name_field = ft.TextField(value=f'{self.option_number}',label=f'Nombre de Opción {self.option_number}')
        self.color_picker = ColorPicker(generate_random_color('hex'))
        self.ref = self
        self.img_path = None
        self.container = parent
        self.prob_field = SliderExample()
        self.selected_files = ft.Text(ref=self,width=105,max_lines=3,overflow=ft.TextOverflow.ELLIPSIS)
        #Buttons to delete images or the instance
        self.del_instance = ft.IconButton( icon=ft.icons.DELETE_FOREVER_ROUNDED, on_click=self.remove_widget, data=0 )
        self.del_image = ft.IconButton( icon=ft.icons.CLOSE_ROUNDED, on_click=self.remove_image)
        
        #FilePicker for images
        self.file_dialog = img_picker
        self.file_dialog.initial_directory = self.img_path
        self.image_field = ft.Row(
                [
                    ft.ElevatedButton(
                        "Selecciona imagen",
                        icon=ft.icons.UPLOAD_FILE,
                        on_click=self.handle_click,
                    ),
                    self.selected_files
                ]
            )
    
    def remove_widget(self,e):
        #Search inside the overlay
        for index,control in enumerate(self.container.controls):
            if control.ref == self.ref:
                    
                #Removes itself from the overlay
                self.container.controls.remove(control)
        e.control.page.update()
        
    def remove_image(self,e):        
        #Removes image from FilePicker
        self.img_path = None
            
        self.selected_files.value = ''
        self.selected_files.update()
        
    def pick_files_result(self,e: ft.FilePickerResultEvent):
        self.selected_files.value = (
            ", ".join(map(lambda f: f.name, e.files)) if e.files else "Cancelled!"
        )
        
        if e.files:
            self.img_path = os.path.relpath(e.files[0].path,os.path.dirname(__file__))
        else:
            self.img_path = None
            
        self.selected_files.update()
        
        
    def handle_click(self,e):
        self.file_dialog.on_result=self.pick_files_result
        
        self.file_dialog.pick_files(
            allowed_extensions=['jpeg','jpg','png','svg','gif'],
            file_type=ft.FilePickerFileType.IMAGE,
            initial_directory = self.img_path
        )
    
    def _before_build_command(self):
        super()._before_build_command()
        # called every time on self.update()
        
        #Checks if it is the last element on the overlay
        if self.container.controls[-1].ref == self.ref:
            self.key = 'last_item'
        else:
            self.key = None
                
        #This helps FilePicker update and maintain it's own state, besides updating the control reference after switching views
        self.build()
         
    def build(self):
        
        image_row = ft.Row(
            [
                self.image_field,
                self.del_image,
            ]
        )
        
        return ft.Column( 
            [
                ft.Row([
                self.name_field,
                self.del_instance,
                ]),
                self.color_picker,
                image_row,
                self.prob_field,
            ],
            ref=self.ref,
            spacing=10,
            wrap=True
        )
        

def main(page: ft.Page):
    page.title = "Define tu ruleta"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    
    ROUTE = ["/","/ruleta"]
    
    def on_keyboard(e: ft.KeyboardEvent):
        # print(e.key)
        full_screen = page.window_full_screen
        if e.ctrl and e.key == 'F':
            page.window_full_screen = not(full_screen)
            page.update()
        if e.key == 'Escape':
            page.window_full_screen = False
            page.update()
        if e.key == ' ' and  page.route == ROUTE[1]:
            if wheel.animation_started == False:
                wheel.animate(e)
            else:
                wheel.stop()
        if e.key == 'Backspace' and page.route == ROUTE[0]:
            if num_options.focused:
                num_options.focus()
                
        if e.key == 'Enter' and page.route == ROUTE[0]:
            if len(overlay.controls) > 0:
                time.sleep(0.2)
                page.views[0].scroll_to(key='last_item',duration=300,curve=ft.AnimationCurve.EASE_IN)
        
        if e.key == 'Tab':
            if page.route == ROUTE[0]:
                load_wheel_configuration(e)
            elif page.route == ROUTE[1]:
                go_to_configuration(e)
         
    page.on_keyboard_event = on_keyboard
    
    #Declaring the container for all the Inputs inside the Application  
    overlay = ft.Row(
        [],
        wrap=True,
        spacing=10,
        run_spacing=10,
        )
    
    #Parse all the data found inside the overlay
    def submit_form():
        forms_data = []
        for control in overlay.controls:
            
            if isinstance(control, OptionForm):
                        
                data = {
                    'title': control.name_field.value,
                    'color': control.color_picker.color,
                    'image': control.img_path, # This will be the path to the uploaded file
                    'probability': control.prob_field.value
                }
                
                forms_data.append(data)
              
        if len(forms_data) > 1:
            return forms_data
    
    # Render a FilePicker to save the data in a .json format
    submit_button = FilePickerExample("Guardar Archivo",data=submit_form,save_file=True)
    
    #Load Data from the selected file
    def load_data(filePicker=None,cleanup=True):
        nonlocal config_load
        
        #Here filePicker argument decides which filePicker object we will use to load the configuration data
        File = filePicker if filePicker != None else config_load
        # print(File.button.text)
        file_path = None
            
        if File.file_picker.result != None and File.file_picker.result.files != None:
                for f in File.file_picker.result.files:
                    file_path = os.path.dirname(f.path+'/'+f.name)
                    
        if file_path != None:            
            with open(file_path) as f:
                #Load Json File
                forms_data = json.load(f)
                #Removes all the other fields from the overlay if cleanup is True
                if cleanup:
                    overlay.clean()
                #Get all the data inside the Json File    
                for i, data in enumerate(forms_data):
                    form = OptionForm(i+1,overlay)
                    form.name_field.value = data['title']
                    form.color_picker.color = data['color']
                    form.img_path = data['image']
                    form.selected_files.value = data['image']
                    form.prob_field.value = data['probability']
                    overlay.controls.append(form)
            
            num_options.value = len(overlay.controls)
            page.update()
              
    #Define both FilePicker that will be used to load the data
    config_load = FilePickerExample('Cargar Nueva Ruleta',callback=load_data)
    load_from_file = FilePickerExample('Añadir desde Archivo',callback=lambda:load_data(load_from_file,cleanup=False),icon=ft.icons.FILE_OPEN_ROUNDED)
    
    num_options = InputField(value=2,text_align=ft.TextAlign.CENTER,label='Ingresa la cantidad de opciones que quieres')
    #Both Keep track of the last autogenerated title inside the overlay
    last_value = 0
    last_option = None
    #Adds Input Fields to the page
    def add_options(e):
        nonlocal last_option
        nonlocal last_value
        
        current_value = normalize_value(num_options.value)
        
        if current_value == None:
            return
        
        position = overlay.controls.__len__()
        # print(position)
        
        if last_option != None and position > 0:
            #Actualizamos el valor antes de asignarlo
            last_option = normalize_value(overlay.controls.__getitem__(-1).controls.__getitem__(0).controls.__getitem__(0).controls.__getitem__(0).value)
            position = last_option if last_option != None else last_value

        if current_value >= 1:
            for i in range(current_value):
                form = OptionForm(position+i+1,overlay)
                
                overlay.controls.append(form)
                last_value = position+i+1
        
        overlay.update()
        
        #Gets the value from the first element (the title) inside the last column
        last_option = normalize_value(overlay.controls.__getitem__(-1).controls.__getitem__(0).controls.__getitem__(0).controls.__getitem__(0).value)
     
    add_button = ft.ElevatedButton("Añadir Opciones",on_click=add_options)
    
    def randomize_positions(e):
        fields = overlay.controls
        random.shuffle(fields)
        overlay.update()
    
    randomize_button = ft.ElevatedButton("Randomizar",on_click=randomize_positions,icon=ft.icons.SHUFFLE_ON_ROUNDED)

    keyboard_shortcuts = ShortcutsDialog("Atajos del Teclado")
    def open_shortcuts(e):
        keyboard_shortcuts.open = True
        e.control.page.update()
        
    show_shortcuts = ft.ElevatedButton("Atajos del Teclado",icon=ft.icons.KEYBOARD,on_click=open_shortcuts)
    #First Row on view 1
    INPUT_ROW = ft.Row(
            [
                ft.Row([
                    ft.Row([
                        num_options,
                        add_button,
                        randomize_button
                    ]),
                    keyboard_shortcuts,
                    show_shortcuts,
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Row([
                    load_from_file,
                    config_load,
                    img_picker,
                ])
            ],
            wrap=True,
            spacing=10,
            run_spacing=10,
        )
    #Dialog used to display the winning option
    dialog = CongratulationsDialog()
    wheel = Wheel(300, 100)
    
    def load_wheel_configuration(e):
        wheel.data = submit_form()
        # print(wheel.data)
        
        if wheel.data != None:
            page.go(ROUTE[1])
            #This wheel update the chart after rendering the view
            wheel.update_sections()
    
    #This opens the Dialog and shows the title of the winning option based on it's probability
    def get_selected_option(e):
        options = wheel.data
        wheel.animation_started = False
        # Extract the options and probabilities
        choices = [option for option in options]
        weights = [option["probability"] for option in options]

        # Select an option based on its probability
        selected_option = random.choices(choices, weights=weights, k=1)[0]
        # print(selected_option)
        
        dialog.title = ft.Text(f"La Opción Ganadora fue! {selected_option['title']}",text_align=ft.TextAlign.CENTER)
        if selected_option['image'] != None:
            dialog.content = ft.Image(selected_option['image'],fit=ft.ImageFit.CONTAIN)
        else:
            dialog.content = None
        dialog.open = True
        page.update()
    
    
    #Show Dialog after animation
    wheel.on_animation_end = get_selected_option
    
    spin_button = ft.ElevatedButton("Spin the Wheel!", on_click=wheel.animate)
    
    #Wheel Customization
    #Slider to change the size of the images
    img_size_slider = SliderExample('px')
    img_size_slider.max_value = 200
    img_size_slider.value = '100'
    
    def size_change():
        wheel.badge_size = img_size_slider.string_value
        # print(wheel.badge_size)
        
        wheel.update_sections(force=True)
        
    img_size_slider.callback = size_change
    
    #Slider to change the duration of the animation
    duration_slider = SliderExample('segundos')
    duration_slider.max_value = 20
    duration_slider.value = '10'
    
    def duration_change():
        wheel.set_duration(duration_slider.string_value*1000)
        # print(wheel.duration)
            
        wheel.update_sections(force=True)
        
    duration_slider.callback = duration_change
    
    #Slider to change the radius of the circle
    radius_slider = SliderExample('px')
    radius_slider.max_value = 600
    radius_slider.value = '300'
    
    def radius_change():
        wheel.radius = radius_slider.string_value
        wheel.container.height = radius_slider.string_value*2
        # print(wheel.radius)
        
        wheel.update_sections(force=True)
        
    radius_slider.callback = radius_change
    
    
    config_wheel_style = ft.Column( 
                        [
                            ft.Text("Tamaño máximo de las imágenes"),
                            img_size_slider,
                            ft.Text("Cuanto Dura la animación"),
                            duration_slider,
                            ft.Text("Radio de la ruleta"),
                            radius_slider,
                        ]
                    )
    
    def go_to_configuration(e):
        page.go(ROUTE[0])       
    
    view1= ft.View(
                ROUTE[0],
                [
                    ft.AppBar(
                        title=ft.Text("Configuración"),
                        bgcolor=ft.colors.SURFACE_VARIANT
                    ),
                    INPUT_ROW,
                    overlay,
                    ft.Row([
                        submit_button,
                        ft.ElevatedButton("Ir a La Ruleta", on_click=load_wheel_configuration),
                    ])
                ],
                scroll=True
            )
    view2 = ft.View(
                    ROUTE[1],
                    [
                        ft.AppBar(title=ft.Text("Ruleta"), bgcolor=ft.colors.SURFACE_VARIANT),
                        ft.ElevatedButton("Ir a Configuración", on_click=go_to_configuration,icon=ft.icons.SETTINGS,top=True),
                        spin_button,
                        wheel.container,
                        config_wheel_style,
                        dialog
                    ],
                    scroll=True
                )
    
    page.views.append(view1)
    page.views.append(view2)
    
    #Add views to page
    def route_change(e):
        
        if page.route == ROUTE[0]:
           view2.visible = False
           view1.visible = True
            
        if page.route == ROUTE[1]:
            view1.visible = False
            view2.visible = True

            wheel.is_mounted = True
            
        page.update()

    #Pop views
    def view_pop(e):
        if page.route == ROUTE[0] and len(overlay.controls) <= 1:
            return
            
        view2.visible = not view2.visible
        view1.visible = not view1.visible
        
        page.update()

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    page.go(page.route)    
    num_options.focus()
    
        
    
ft.app(target=main)
