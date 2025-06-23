# main.py
import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivy.properties import StringProperty, NumericProperty, ListProperty
from kivy.utils import platform
from kivy.lang import Builder

import json
import os
import time
import random
from datetime import datetime, date # Import datetime for date tracking

# Plyer for notifications
# Make sure to add plyer to your buildozer.spec requirements!
# requirements = python3,kivy,plyer
if platform == 'android':
    from plyer import notification
    # For Android permissions, you might need to add these to buildozer.spec:
    # android.permissions = VIBRATE, RECEIVE_BOOT_COMPLETED, FOREGROUND_SERVICE
    # Although RECEIVE_BOOT_COMPLETED and FOREGROUND_SERVICE aren't fully utilized for a persistent background service here.
else:
    # Mock notification for desktop testing
    class MockNotification:
        def notify(self, title='', message='', app_name='', app_icon='', timeout=10, toast=False):
            print(f"Mock Notification: {title} - {message}")
    notification = MockNotification()

kivy.require('2.0.0')

# Load the KV file explicitly
Builder.load_file('tor_baap.kv')


# --- Global Data Storage ---
DATA_FILE = 'tor_baap_data.json' # Will store screen time and last reset date

def load_data():
    """Loads screen time data and last reset date from a JSON file."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Ensure keys exist, provide defaults if not
            return {
                "total_screen_seconds": data.get("total_screen_seconds", 0),
                "last_reset_date": data.get("last_reset_date", datetime.min.strftime("%Y-%m-%d")) # Default to min date
            }
    return {"total_screen_seconds": 0, "last_reset_date": datetime.min.strftime("%Y-%m-%d")}

def save_data(data):
    """Saves screen time data and last reset date to a JSON file."""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# --- The Unhinged Toxic Notifications ---
toxic_notifications = [
    {"title": "🚨 Screen On, Brain Off?!", "message": "Phone haate ki koros? Insta scroll korle ki porikkha diye dibi? Chol, phone rakh, kajer kotha bolchi! Tor future TikTok e hobe na!"},
    {"title": "⚠️ Lagging Life Detected!", "message": "Ei, tor screen time Amar future er theke beshi hoye jacche! Ajke pora sesh na korle, tor WiFi password Amar haate chole asbe! Shuru kor!"},
    {"title": "🚫 Distraction Overload!", "message": "Tor screen addiction Google er algorithms ke har manay dicche! Eto time phone e dile kemon hobe? Ajke pora sesh na korle, tor favorite streaming service off kore dibo, ami Bolchi!"},
    {"title": "👴 Baap er Warning!", "message": "Mone hochhe tui amar thekeo beshi phone e thakish? Porle na, jibone kisu korbi na. Tor future kobor e jay, amake dosh dis na! Ajke pora sesh na korle, shob social media account delete. Last warning!"},
    {"title": "🎮 Game Over, IRL!", "message": "Ki holo? Phone dhorle ki level up hobe? Chol, pora dhor, jibone level up kor! Na porle, tor next game launch e beta test korte parbi na!"},
    {"title": "😴 Naki Ghum Peyeche?", "message": "Phone ghantar por ghanta! Eto energy kothay pash? Porashona korar somoy ki ghumiye porish? Ja, mukh dhuye aa, pora shuru kor!"},
    {"title": "🔥 Tor Future Jalano Shuru!", "message": "Jodi eivabe phone tipte thakish, tor degree r Facebook status ek hobe! Chol, desk e bosh, kichu productive kor!"},
    {"title": "🛑 Stop & Think!", "message": "Ki dekhchis? Meme? Reel? Ei shob pore tor bank balance e ki asbe? Porashona kor, taka asbe! Jaa!"},
    {"title": "🤖 Ami Dekhtesi!", "message": "Tui vabchis ami jani na ki korchis? Amar chokh tor shob activity track kore! Porashona kor, na hole ami action nibo!"},
    {"title": "🚀 Speed Up, Buttercup!", "message": "Tor phone chalano speed jodi porashonay dito, tui ekhon Einstein hotish! Chol, speed barah, porashonay!"},
    {"title": "🚫 Phone Mukhe Dhokanor Chesta Koros Naki?", "message": "Eto phone e thakle chokh kharap hobe, bujhli?! Chokh diye phone khawa jabe na! Porashona kor!"},
    {"title": "⏰ Time Is Money, But Tor Time Is MEME!", "message": "Jibone ekta boro kichu korbi na, shudu phone tipbi? Eto time loss korle pore pachtabi! Chol, uth!"},
    {"title": "🚨 Urgent: Life Under Threat!", "message": "Tor screen time chart ekta rollercoaster! Utha-nama korbe na, shudhu niche namuk! Phone rakh! Ami bolchi!"},
    {"title": "🤯 Matha Kharap Hoye Jabbe!", "message": "Eto phone use korle matha ghurbe, porashona kothay?! Jaa, aktu baire theke ghur, ar tarpor pora shuru kor!"},
    {"title": "🔥 Tor Baap Always Watching!", "message": "Na porle, ami jani ki korte hobe. Tor phone e virus dhukiye dibo. Valo hobe porashona korle!"},
    {"title": "💀 Tor Atta Shantite Thakuk!", "message": "Eto phone use korle tor jibon theke ami chole jabo. Porashona kor, na hole tor atta o shanti pabe na!"},
    {"title": "🚷 Danger: Offline Zone!", "message": "Tui ki vabchis tui phone er moddhe dhuke jabi? Offline hosh, jibon ektu dekh! Porashona kor!"},
    {"title": "🧠 Brain.exe Has Stopped Working.", "message": "Eto phone tipte tipte tor matha hang hoye gelo naki? Restart kor nijeke, porashonay focus kor!"},
    {"title": "📉 Performance Alert!", "message": "Tor jiboner performance graph phone er jonne niche namche. Upar uthte chaile phone rakh, pora shuru kor!"},
    {"title": "👿 Na Porle Shob Ses!","message": "Ajke pora sesh na korle tor Google account delete kore dibo. Gmail, YouTube, even tor Drive — shob uray dibo. Ready?"},
    {"title": "⚰️ Kobor Ready Ache!","message": "Na porle kobor e giye boi porbi. Math er chapter oikhane shesh hobe, but time thakbe na, bujhlis?"},
    {"title": "📵 Boi Open, Na Hole Phone Lock!","message": "Tui boi khulbi na? Bujhte parchi. Phone-er bootloader diye lock kore dibo, password niye jabo akashbani te."},
    {"title": "🔥 Nuclear Uncle Activated!","message": "Tui jodi akhon pora na shuru korish, ami tor WiFi router e nuke drop kore dibo. Internet e blackout, life e darkness."},
    {"title": "🪓 Last Warning!","message": "Ajke pora na korle tor favorite game er save data delete kore dibo. Tor Minecraft-er bari ekhn theke biday!"},
    {"title": "💣 TikTok-er Shesh Gonta!","message": "Pora na korle, tor TikTok account ke report diye terminate kore debo. Next time dance korish boi er opor boshe." },
    {"title": "☠️ Tor Matha Restart Lagbe!","message": "Eto phone tipte tipte CPU overheated. Boi por na hole, RAM clear kore dibo permanently!"},
    {"title": "📚 Porashona Kortei Hobe!","message": "Na porle amar sathe chemistry practical hobe — acid diye reaction korbo tor phone er screen-e."},
    {"title": "🧟‍♂️ Tor Future Zombie Mode!","message": "Pora na korle future e tor AI replace kore dibe. Tui thakbi McDonald’s er cashier, AI dibe math solution."},
    {"title": "🔒 Tor Brain Lock!","message": "Ajke pora na korle tor brain e lock lagbe. Password hint: 'Ami porashona kori na' — guess korle o open hobe na!"},
    {"title": "💀 Tor IQ on Vacation!","message": "Tor brain to offline ache mone hoy! Jibone ektu smart hote chaile, phone theke ber hoye book er moddhe dhuk!"},
    {"title": "📴 National Uselessness Alert!","message": "Phone tipte tipte tor hands er fingerprint er o identity crisis hoye jacche! Chol, kajer kichu kor." },
    {"title": "🔞 Phone Addiction = Brain Degeneration","message": "Ei bhabe jodi choltay thakis, tor brain age restricted hoye jabe! Grow up. Study up."},
    {"title": "👹 Shaitani Mode Activated!","message": "Tui jani na, ami jani! Tui ekhon ei notification bondho korte chaichhis. But guess what? Porashona korle ami chup thakbo."},
    {"title": "🎯 Tor Target Kothay?","message": "Je goal tor chhilo, setar naam o bhule gasos naki? Insta r Reel diye GPA ashe na re baba!"}
    
]

class ScreenTimeTracker:
    """Manages tracking and reporting of app-specific screen time."""
    def __init__(self):
        self.total_screen_seconds = 0 # Total cumulative seconds this app was in foreground
        self.session_start_time = 0  # Timestamp when the app became active (foreground)
        self.last_reset_date = datetime.min.date() # Date of last reset, initialized to min date

    def load_progress(self):
        """Load the saved total screen time and last reset date."""
        data = load_data()
        self.total_screen_seconds = data.get("total_screen_seconds", 0)
        # Convert string date back to date object
        self.last_reset_date = datetime.strptime(data.get("last_reset_date"), "%Y-%m-%d").date()
        print(f"Loaded total screen seconds: {self.total_screen_seconds}, Last reset date: {self.last_reset_date}")

    def save_progress(self):
        """Save the current total screen time and current date."""
        data = {
            "total_screen_seconds": self.total_screen_seconds,
            "last_reset_date": self.last_reset_date.strftime("%Y-%m-%d") # Store date as string
        }
        save_data(data)
        print(f"Saved total screen seconds: {self.total_screen_seconds}, Last reset date: {self.last_reset_date}")

    def on_app_resume(self):
        """Called when the app resumes from pause/background."""
        print("App Resumed!")
        current_date = date.today()
        # Check if it's a new day since the last reset
        if current_date > self.last_reset_date:
            print(f"New day detected! Current date: {current_date}, Last reset date: {self.last_reset_date}")
            self.reset_for_new_day() # Automatic midnight reset triggered here
        
        self.session_start_time = time.time()
        self.send_random_toxic_notification() # Send notification every time app is opened/resumed

    def on_app_pause(self):
        """Called when the app goes to pause/background."""
        print("App Paused!")
        if self.session_start_time != 0:
            time_spent_in_session = time.time() - self.session_start_time
            self.total_screen_seconds += time_spent_in_session
            self.session_start_time = 0 # Reset session start time
            self.save_progress()
            print(f"Session time: {time_spent_in_session:.2f}s, Total: {self.total_screen_seconds:.2f}s")

    def on_app_stop(self):
        """Called when the app is about to close."""
        print("App Stopping!")
        # Ensure any active session time is saved before app terminates
        self.on_app_pause()

    def format_time(self, seconds):
        """Formats seconds into HH:MM:SS string."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        return f"{hours:02}:{minutes:02}:{seconds:02}"

    def send_random_toxic_notification(self):
        """Sends a random toxic screen time notification."""
        n = random.choice(toxic_notifications)
        notification.notify(
            title=n["title"],
            message=n["message"],
            app_name="Tor Baap",
            # app_icon='path/to/your/icon.png' # Optional: Add an icon path here for Android build
        )
        print(f"Notification sent: {n['title']}")

    def send_progress_report_notification(self, is_daily_reset=False):
        """Sends a notification with today's screen time progress."""
        if is_daily_reset:
            # Report for the just-ended day
            title_prefix = "⏰ Ajker Screen Time Report: Kheyal Rakhis!"
            message_suffix = "Ei time ajker jonno lock hoye gelo. Kal theke abar shuru hobe! Bhalo hoye ja, na hole ami jani ki korte hoy!"
        else:
            # Standard update on app open, not necessarily a reset
            title_prefix = "⏰ Current Screen Time Update:"
            message_suffix = "Eto time phone e? Kisu kor, tor future ache! "

        # Craft the message using previous day's data if it's a reset
        # Note: self.total_screen_seconds will already be the previous day's total BEFORE it's reset
        # if this function is called by reset_for_new_day().
        progress_message = f"{title_prefix}\nAjke tor total screen time {self.format_time(self.total_screen_seconds)}. {message_suffix}"
        
        notification.notify(
            title=title_prefix,
            message=progress_message,
            app_name="Tor Baap",
            # app_icon='path/to/your/icon.png' # Optional: Add an icon path here for Android build
        )
        print(f"Progress Report sent: {progress_message}")

    def reset_for_new_day(self):
        """Resets the screen time progress for a new day (automatic)."""
        print("Resetting for a new day...")
        # Send progress report *before* resetting self.total_screen_seconds
        # This way, the report shows the *previous* day's total.
        self.send_progress_report_notification(is_daily_reset=True)
        self.total_screen_seconds = 0
        self.last_reset_date = date.today() # Update last reset date to today's date
        self.save_progress() # Save the reset state and new date
        print("Progress reset and saved for new day.")


class MainScreen(Screen):
    """The main screen of the application."""
    display_time = StringProperty("00:00:00")
    tracker = None # Will be set by the app instance
    background_color = ListProperty([0.05, 0.05, 0.05, 1]) # Darker background

    def on_enter(self, *args):
        """Called when the screen becomes active."""
        if self.tracker:
            self.update_display_time(0) # Initial update
            # Schedule periodic update for the display time
            Clock.schedule_interval(self.update_display_time, 1)

    def update_display_time(self, dt):
        """Updates the time displayed on the screen."""
        if self.tracker and self.tracker.session_start_time != 0:
            current_session_time = time.time() - self.tracker.session_start_time
            total_current_display_time = self.tracker.total_screen_seconds + current_session_time
        elif self.tracker:
            total_current_display_time = self.tracker.total_screen_seconds
        else:
            total_current_display_time = 0

        self.display_time = self.tracker.format_time(total_current_display_time)


class TorBaapApp(App):
    """Main Kivy application class."""
    def build(self):
        self.title = "Tor Baap"
        self.icon = 'icon.png' # Optional: Your app icon for Android
        self.tracker = ScreenTimeTracker()
        self.tracker.load_progress()

        sm = ScreenManager()
        main_screen = MainScreen()
        main_screen.tracker = self.tracker
        sm.add_widget(main_screen)
        return sm

    def on_start(self):
        """Called when the app starts."""
        print("App starting!")
        # on_start implicitly means the app is in foreground
        self.tracker.on_app_resume() # This will trigger the new day check and notification

    def on_pause(self):
        """Called when the app is sent to background or another app comes foreground."""
        print("App pausing!")
        self.tracker.on_app_pause()
        return True # Return True to allow the app to be paused (kept alive in background)

    def on_resume(self):
        """Called when the app resumes from pause."""
        print("App resuming!")
        self.tracker.on_app_resume() # This will trigger the new day check and notification

    def on_stop(self):
        """Called when the app is about to be terminated."""
        print("App stopping!")
        self.tracker.on_app_stop()
        # Unschedule the clock event to prevent errors after app termination
        Clock.unschedule(self.root.get_screen('main_screen').update_display_time)


if __name__ == '__main__':
    TorBaapApp().run()
