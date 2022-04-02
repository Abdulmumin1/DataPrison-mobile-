from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.uix.list import TwoLineListItem, OneLineAvatarListItem
from kivymd.uix.card import MDCard, MDCardSwipe
from kivymd.uix.label import MDLabel
from kivymd.uix.bottomsheet import MDListBottomSheet, MDGridBottomSheet
from kivy.core.clipboard import Clipboard
from kivy.core.window import Window
from kivy.clock import Clock
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.snackbar import Snackbar
from kivymd.utils import asynckivy
from kivymd.toast import toast
import threading
import json
from os.path import exists

from manager import all_website, create_table, delete_website, register_password, search_website, update_password_entry
from utils import write_cache, read_cache, update_cache, search_data

text = None
secondary_text = None
data_id = None
current_widget = None
cache_data = None


class LoginScreen(Screen):
    ""


class PasswordScreen(Screen):
    ""


class RegisterScreen(Screen):
    ""


class ItemConfirm(OneLineAvatarListItem):
    ""


# class SwipeToDeleteItem(MDCardSwipe):
#     content = PasswordItem()


class PasswordItem(TwoLineListItem):
    def __init__(self, datas):
        super().__init__()
        self.text = datas[0]
        self.secondary_text = datas[1]
        self.data_id = datas[2]
        self.bs = None
        self.delete_dialog = None
        self.edit_dialog = None

    def on_release(self):
        global text, secondary_text, data_id, current_widget
        text, secondary_text, data_id, current_widget = self.text, self.secondary_text, self.data_id, self
        app.main_screen.add_b_sheet()


class RegDialog(MDCard):
    def __init__(self, datas=False):
        super().__init__()
        self.orientation = 'vertical'
        self.spacing = 5
        self.padding = 10
        # self.size_hint_y = None

        self.size_hint = (.9, .38)
        self.radius = (0, 0, 10, 10)
        self.elevation = 10
        # self.opacity = 8
        label_text = "Register" if not datas else "Edit"
        self.label = MDLabel(text=label_text, font_style="H4", halign="center")
        self.title_text = MDTextField(hint_text='Title')
        self.value_text = MDTextField(hint_text='Content')
        options_layout = MDBoxLayout()
        ok, cancel = [MDRaisedButton(text="Ok",
                      on_release=lambda x:app.main_screen.save_entry(datas)),
                      MDFlatButton(text="Cancel",
                      on_release=lambda x: app.main_screen.ps_widgets_state(False))]
        if datas:
            self.title_text.text = datas[0]
            self.value_text.text = datas[1]

        self.add_widget(self.label)
        self.add_widget(self.title_text)
        self.add_widget(self.value_text)
        options_layout.add_widget(ok)
        options_layout.add_widget(cancel)
        self.add_widget(options_layout)


class MainScreens(ScreenManager):
    def __init__(self):
        super().__init__()
        # load the user config file
        if exists('.user_conf.json'):
            # set to login screen to current screen
            self.create_login_screen()
        else:
            # create and load the register screen and create table
            self.register_screen = RegisterScreen()
            self.add_widget(self.register_screen)
            self.current = 'register'
            create_table()
            register_password('Hi There', 'delete this later')

    def create_login_screen(self):
        self.login_screen = LoginScreen()
        self.add_widget(self.login_screen)
        self.current = 'login'

    def login_in_user(self):
        # get the entered password from login screen
        user_p = self.login_screen.ids.p_log
        user_conf = json.load(open('.user_conf.json'))
        confirm_p = user_conf['user-pass']
        # compare entered password to password stored
        if user_p.text == confirm_p:
            self.password_screen = PasswordScreen()
            self.add_widget(self.password_screen)
            self.current = 'main'
            self.remove_widget(self.login_screen)

            # get the password widget from password screen
            Clock.schedule_once(self.wait_and_load, 1)
            # thread = threading.Thread(
            #     target=all_website, args=(self.create_p_item,))
            # thread.start()
            # for i in self.all_site_reg:
            #     self.create_p_item(i)
            self.dialog = None
            self.continue_searching = True

        else:
            user_p.text = ''

    def wait_and_load(self, *args):
        asynckivy.start(self.load_datas())

    async def load_datas(self):
        self.p_widget = self.password_screen.ids.p_list

        if exists('cache_data.json'):
            saved_data = read_cache()
            global cache_data
            cache_data = read_cache(fmt=False)

        else:
            saved_data = all_website()
            write_cache(saved_data)
        for data in saved_data:
            await asynckivy.sleep(0)
            self.create_p_item(data)

    def register_user(self):
        pas1 = self.register_screen.ids.pas1
        pas2 = self.register_screen.ids.pas2

        password_value = pas1.text
        verify_value = pas2.text
        if password_value and verify_value:
            if password_value == verify_value:
                if len(password_value) < 5:
                    erro_widget = self.register_screen.ids.register_error
                    erro_widget.text = "password must be greater than 5"

                    return
                json.dump({'user-pass': password_value},
                          open('.user_conf.json', 'w'))

                self.create_login_screen()
                self.remove_widget(self.register_screen)
            else:
                erro_widget = self.register_screen.ids.register_error
                erro_widget.text = "password not match"
                pas2.text = ''

    def create_p_item(self, i):
        p_card = PasswordItem(i)
        self.p_widget.add_widget(p_card)

    def add_b_sheet(self):
        bs = MDListBottomSheet()
        bs.radius_from = "top"
        bs.radius = 80
        bs.animation = True
        bs.duration_opening = .01
        data = {
            text: "panorama-fisheye",
            'Copy': 'content-copy',
            'Delete': 'delete-outline',
            'Edit': 'circle-edit-outline'
        }
        for item in data.items():

            bs.add_item(item[0], callback=lambda x, y=item[1]
                        : self.callbacks(y), icon=item[1])
        bs.open()

    def show_del_dialog(self):
        if not self.dialog:
            self.dialog = MDDialog(
                text='Entry for {} will be deleted?'.format(text),
                buttons=[
                    MDFlatButton(
                        text="CANCEL", on_release=lambda x:self.dismiss_dialogs()),
                    MDRaisedButton(
                        text="OK", on_release=lambda x:self.delete_and_remove())
                ]
            )
            self.dialog.open()

    def dismiss_dialogs(self):
        self.dialog.dismiss()
        self.dialog = None

    def show_write_dialog(self, edit=None):
        if not self.dialog:
            self.dialog = RegDialog(edit)
            # self.password_screen.opacity = .1
            self.ps_widgets_state(True)
            self.password_screen.add_widget(self.dialog)
            # move dialog to the top
            self.dialog.pos_hint = {"top": .96, "center_x": .5}
        else:
            self.dialog = None

    def save_entry(self, edit_values=None):
        # get the title and item to save to database

        # When ok is pressed the text and secondary text are global variables
        # set by the widget to the values of it title text and password text
        web_text = self.dialog.title_text.text
        paswrd_text = self.dialog.value_text.text

        if edit_values:
            self.update_entry(web_text, paswrd_text, data_id)
            update_cache(id=data_id, data=[web_text, paswrd_text, data_id])
            return
        if web_text and paswrd_text:
            saved = register_password(web_text, paswrd_text)
            update_cache(datas=saved)

            if saved:
                # enable widgets
                self.ps_widgets_state(False)
                self.bar('Entry for {} created'.format(web_text))
                self.p_widget.clear_widgets()
                Clock.schedule_once(self.wait_and_load, 1)

    def ps_widgets_state(self, state):
        # change state of widgets -> diabled or enabled
        # if state:
        #     self.password_screen.ids.refresh_layout.disabled = True
        # else:
        #     self.password_screen.ids.refresh_layout.disabled = False

        for awidget in self.password_screen.ids.top_card.children:
            awidget.disabled = state
        for widget in self.password_screen.ids.p_list.children:
            widget.disabled = state
        self.password_screen.ids.float_button.disabled = state
        if not state:
            self.password_screen.remove_widget(self.dialog)
            self.dialog = None

    def delete_and_remove(self):
        # delete the entry with the current data id
        # and remove the current widget clicked from the p_widget
        delete_website(data_id)
        data = all_website()
        write_cache(data)
        self.p_widget.remove_widget(current_widget)

        self.bar(f'Entry for {text} deleted')
        self.dismiss_dialogs()

    def callbacks(self, *args):
        if args[0] == 'content-copy':
            Clipboard.copy(secondary_text)
            toast('copied')
        elif args[0] == 'delete-outline':
            self.show_del_dialog()
        elif args[0] == 'circle-edit-outline':
            # title text and value text of the widget clicked
            # which is stored in a global variable text and secondary text
            self.show_write_dialog((text, secondary_text))

    def update_entry(self, title_text, value_text, id):
        update_password_entry(title_text, value_text, id)
        self.ps_widgets_state(False)
        # update the widget
        widget = current_widget
        widget.text = title_text
        widget.secondary_text = value_text
        self.bar(f'Entry for {title_text} updated')

    def search_data(self):
        if not cache_data:
            return
        q = self.password_screen.ids.search_field_id.text
        returned_search = search_data(q, datas=cache_data)
        if returned_search:
            self.p_widget.clear_widgets()
            for w in returned_search:
                self.create_p_item(w)

    # def refresh_callback(self, *args):
    #     '''A method that updates the state of your application
    #     while the spinner remains on the screen.'''
    #     self.p_widget.clear_widgets()

    #     def refresh_callback(interval):
    #         self.wait_and_load()
    #         self.password_screen.ids.refresh_layout.refresh_done()
    #         self.tick = 0
    #     Clock.schedule_once(refresh_callback, 1)

    def bar(self, text):
        snackbar = Snackbar(
            text=text,
            snackbar_x="10dp",
            snackbar_y="10dp",)
        snackbar.size_hint_x = (
            Window.width - (snackbar.snackbar_x * 2)) / Window.width
        snackbar.open()


class MainApp(MDApp):
    def save_stuff(self):
        if self.theme_cls.theme_style == 'Light':
            self.theme_cls.theme_style = 'Dark'
        else:
            self.theme_cls.theme_style = 'Light'
        self.change_palatte()

    def save_bg(self, what):
        with open('.datas.txt', 'w') as conf_file:
            conf_file.write(what)

    def on_start(self):

        if not exists('.datas.txt'):

            self.theme_cls.theme_style = 'Light'
            # self.theme_cls.primary_hue = '800'
            self.app_style = 'Light'
        else:
            _file = open('.datas.txt')
            st = _file.readline()

            st = st.strip()
            _file.close()
            self.theme_cls.theme_style = st

        self.change_palatte()

    def change_palatte(self):
        if self.theme_cls.theme_style == 'Light':
            self.theme_cls.primary_palette = 'Teal'
        else:
            self.theme_cls.primary_palette = 'Amber'

    def on_pause(self):
        self.save_bg(self.theme_cls.theme_style)

    def on_stop(self):
        self.save_bg(self.theme_cls.theme_style)

    def build(self):
        self.main_screen = MainScreens()
        return self.main_screen


app = MainApp()
app.run()
