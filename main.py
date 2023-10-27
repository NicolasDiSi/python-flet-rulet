import flet as ft
from flet_contrib.color_picker import ColorPicker


import colour
import random
import json
import os

#Interfaz
from Interface import CongratulationsDialog, FilePickerExample, SliderExample, Wheel, normalize_value

def generate_random_color(format):
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    if format == 'hex':
        return colour.rgb2hex((r,g,b))
    else:
        return tuple(r,g,b)

class OptionForm(ft.UserControl):
    
    def __init__(self, option_number,parent,**kwargs):
        super().__init__(**kwargs)
        self.option_number = option_number
        self.name_field = ft.TextField(value=f'{self.option_number}',label=f'Nombre de Opción {self.option_number}')
        self.color_picker = ColorPicker(generate_random_color('hex'))
        self.ref = self
        self.img_path = None
        self.prob_field = SliderExample()
        self.container = parent
        self.selected_files = ft.Text(width=105)
        #Buttons to delete images or the instance
        self.del_instance = ft.IconButton( icon=ft.icons.DELETE_FOREVER_ROUNDED, on_click=self.remove_widget, data=0 )
        self.del_image = ft.IconButton( icon=ft.icons.CLOSE_ROUNDED, on_click=self.remove_image)
        
        #FilePicker for images
        self.file_dialog = ft.FilePicker(self,on_result=self.pick_files_result)
        self.file_dialog.initial_directory = self.img_path
        self.image_field = ft.Row(
                [
                    ft.ElevatedButton(
                        "Selecciona imagen",
                        icon=ft.icons.UPLOAD_FILE,
                        on_click=self.pick_files,
                    ),
                    self.selected_files
                ]
            )
        
    def remove_widget(self,e):
        # e.control.page.remove()
        
        #Removes itself from the overlay
        for control in self.container.controls:
                
            if control.ref == self.ref:
                self.container.controls.remove(control)
        e.control.page.update()
        
    def remove_image(self,e):        
        #Removes image from FilePicker
        if self.file_dialog.result != None:
            self.file_dialog.result.files.clear()
        self.selected_files.value = ''
        self.selected_files.update()
        
    def pick_files_result(self,e: ft.FilePickerResultEvent):
        self.selected_files.value = (
            ", ".join(map(lambda f: f.name, e.files)) if e.files else "Cancelled!"
        )
        self.selected_files.update()
            
        
    def pick_files(self,e):
        self.file_dialog.pick_files(
            allowed_extensions=['jpeg','jpg','png','svg','gif'],
            file_type=ft.FilePickerFileType.IMAGE
        )
        
    def build(self):
        
        image_row = ft.Row(
            [
                self.image_field,
                self.del_image,
            ]
        )
        
        return ft.Column( 
            [
                self.name_field,
                self.color_picker,
                self.file_dialog,
                image_row,
                self.prob_field,
                self.del_instance
            ],
            ref=self.ref,
            spacing=10,
            wrap=True
        )
        

def main(page: ft.Page):
    page.title = "Define tu ruleta"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    
    #Parse all the data found inside the overlay
    def submit_form():
        forms_data = []
        for control in overlay.controls:
            image = None
            # print(control)
            if isinstance(control, OptionForm):
                if control.file_dialog.result != None and control.file_dialog.result.files != None:
                    for f in control.file_dialog.result.files:
                        image = os.path.dirname(f.path+'/'+f.name)
                        # print(image)
                        
                data = {
                    'title': control.name_field.value,
                    'color': control.color_picker.color,
                    'image': image, # This will be the path to the uploaded file
                    'probability': control.prob_field.value
                }
                
                forms_data.append(data)
              
        if len(forms_data) > 1:
            return forms_data
    
    # Render a FilePicker to save the data in a .json format
    submit_button = FilePickerExample("Guardar Archivo",data=submit_form,save_file=True)
    
    #Declaring the container for all the Inputs inside the Application  
    overlay = ft.Row(
        [],
        wrap=True,
        spacing=10,
        run_spacing=10,
        )
    
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
                num_options.value = len(forms_data)
                #Removes all the other fields from the overlay if cleanup is True
                if cleanup:
                    overlay.clean()
                #Get all the data inside the Json File    
                for i, data in enumerate(forms_data):
                    form = OptionForm(i+1,overlay)
                    form.name_field.value = data['title']
                    form.color_picker.color = data['color']
                    form.img_path = data['image']
                    form.prob_field.value = data['probability']
                    overlay.controls.append(form)
            page.update()
              
    #Define both FilePicker that will be used to load the data
    config_load = FilePickerExample('Cargar Nueva Ruleta',callback=load_data)
    load_from_file = FilePickerExample('Añadir desde Archivo',callback=lambda:load_data(load_from_file,cleanup=False),icon=ft.icons.FILE_OPEN_ROUNDED)
    
    num_options = ft.TextField(value=2,text_align=ft.TextAlign.CENTER,label='Ingresa la cantidad de opciones que quieres')
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
            last_option = normalize_value(overlay.controls.__getitem__(-1).controls.__getitem__(0).controls.__getitem__(0).value)
            position = last_option if last_option != None else last_value

        if current_value >= 1:
            for i in range(current_value):
                form = OptionForm(position+i+1,overlay)
                
                overlay.controls.append(form)
                last_value = position+i+1
        
        overlay.update()
        
        #Gets the value from the first element (the title) inside the last column
        last_option = normalize_value(overlay.controls.__getitem__(-1).controls.__getitem__(0).controls.__getitem__(0).value)
        
    add_button = ft.ElevatedButton("Añadir Opciones",on_click=add_options)
    
    #First Row on view 1
    INPUT_ROW = ft.Row(
            [
                ft.Row([
                    num_options,
                    add_button,
                ]),
                ft.Row([
                    load_from_file,
                    config_load,
                ])
            ],
            wrap=True,
            spacing=10,
            run_spacing=10,
        )
    #Dialog used to display the winning option
    dialog = CongratulationsDialog()
    
    def load_wheel_configuration(e):
        wheel.data = submit_form()
        # print(wheel.data)
        
        if wheel.data != None:
            page.go("/ruleta")
            #This wheel update the chart after rendering the view
            wheel.update_sections()
        page.update()
    
    #This opens the Dialog and shows the title of the winning option based on it's probability
    def get_selected_option(e):
        options = wheel.data
        # Extract the options and probabilities
        choices = [option for option in options]
        weights = [option["probability"] for option in options]

        # Select an option based on its probability
        selected_option = random.choices(choices, weights=weights, k=1)[0]
        # print(selected_option)
        
        dialog.title = ft.Text(f"La Opción Ganadora fue! {selected_option['title']}",text_align=ft.TextAlign.CENTER)
        if selected_option['image'] != None:
            dialog.content = ft.Image(selected_option['image'],fit=ft.ImageFit.CONTAIN)
            
        dialog.open = True
        page.update()
    
    wheel = Wheel(300, 100)
    #Show Dialog after animation
    wheel.on_animation_end = get_selected_option
    
    spin_button = ft.ElevatedButton("Spin the Wheel!", on_click=wheel.animate)
    
    #Wheel Customization
    img_size_slider = SliderExample('px')
    img_size_slider.max_value = 200
    def size_change():
        wheel.badge_size = img_size_slider.string_value
        # print(wheel.badge_size)
        
        wheel.update_sections(force=True)
        
    img_size_slider.callback = size_change
    
    duration_slider = SliderExample('segundos')
    duration_slider.max_value = 20
    
    def duration_change():
        wheel.set_duration(duration_slider.string_value*1000)
        # print(wheel.duration)
            
        wheel.update_sections(force=True)
        
    duration_slider.callback = duration_change
    
    radius_slider = SliderExample('px')
    radius_slider.max_value = 600
    
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
                            radius_slider
                        ]
                    )
    
    def go_to_configuration(e):
        page.go("/")
        page.update()        
    
    
    view1= ft.View(
                "/",
                [
                    ft.AppBar(title=ft.Text("Configuración"), bgcolor=ft.colors.SURFACE_VARIANT),
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
                    "/ruleta",
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
    
    #Add views to page
    def route_change(e):
        page.views.clear()
        page.views.append(view1)
        if page.route == "/ruleta":
            page.views.append(view2)
            wheel.is_mounted = True
        page.update()

    #Pop views
    def view_pop(e):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    page.go(page.route)
    
    num_options.focus()
    
        
    
ft.app(target=main)
