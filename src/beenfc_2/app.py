"""
BeeNFC 2
"""

import toga
from toga.style.pack import COLUMN, ROW
import platform
import sys

from java import jclass, static_proxy, Override, jvoid, cast, dynamic_proxy
from java.lang import Object
from androidx.core.util import Consumer

if toga.platform.current_platform == "android":
#    from chaquopy import Java
#    from java import jclass, static_proxy
#    from java.lang import Object
#    from androidx.core.util import Consumer
#    from chaquopy.static_proxy import static_proxy
    NfcAdapter = jclass('android.nfc.NfcAdapter')
    Intent = jclass('android.content.Intent')
    PendingIntent = jclass('android.app.PendingIntent')
    IntentFilter = jclass('android.content.IntentFilter')
    Calendar = jclass("java.util.Calendar")


class BeeNFC_2(toga.App):
    def startup(self):
        """Construct and show the Toga application.

        Usually, you would add your application to a main content box.
        We then create a main window (with a name matching the app), and
        show the main window.
        """
        main_box = toga.Box()

        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = main_box

        button = toga.Button(
            "Say Hello!",
            on_press=self.say_hello,
            margin=5,
        )
        main_box.add(button)
        self.label = toga.Label("")
        main_box.add(self.label)

        self.main_window.show()

    def say_hello(self, widget):
        if toga.platform.current_platform != "android":
            self.label.text = "Not Android is: %s (%s) " % (platform.system(), toga.platform.current_platform)
            return
        print("Getting MainActivityClass")
        MainActivityClass = jclass("org.beeware.android.MainActivity")
        print("Getting singletonThis")
        self.activity = MainActivityClass.singletonThis
        print("Getting context")
        self.context = self.activity.getApplicationContext()
        print("Getting nfc_adapter")
        self.nfc_adapter = NfcAdapter.getDefaultAdapter(self.context)
        if not self.nfc_adapter:
            self.label.text = "NFC not available"
            return
        else:
            print("Got NFC adapter")
            self.label.text = "Got NFC adapter"

        print("Got Intents")
        # Create a PendingIntent to start your app when an NFC tag is discovered
        intent = Intent(self.context, self.activity.getClass())
        intent.setFlags(Intent.FLAG_ACTIVITY_SINGLE_TOP)
#        intent.setFlags(PendingIntent.FLAG_IMMUTABLE)
        print("Flags set")
        self.pending_intent = PendingIntent.getActivity(
            self.context, 0, intent, PendingIntent.FLAG_IMMUTABLE)
        
        # Create an intent filter for detecting NFC tags
        print("Creating intent filter")
        nfc_intent_filter = IntentFilter(NfcAdapter.ACTION_TAG_DISCOVERED)
        self.nfc_intent_filter = [nfc_intent_filter]

        print("Enabling foreground dispatch")
        self.nfc_adapter.enableForegroundDispatch(
            self.activity, self.pending_intent, self.nfc_intent_filter, None)

        # Bind activity lifecycle events to properly manage NFC (pause/resume)
        print("Binding -> adding new Intent Listener")
#        print(dir(self.activity))
#        self.activity.bind(on_new_intent=self.on_new_intent)
        self.intentHandler = HandleIntent(self.on_new_intent)
        self.activity.addOnNewIntentListener(self.intentHandler)
        print("Done")
        self.label.text = "NFC Adapter all setup"

    def on_new_intent(self, intent):
        # This method is called when an NFC intent is received
        print("On new intent ran")
        action = intent.getAction()
        print("Action: %s" % action)
        if action == NfcAdapter.ACTION_TAG_DISCOVERED:
            print("NFC discovered")
            self.label.text = "Tag discovered"

# @static_proxy(Consumer)
class HandleIntent(dynamic_proxy(Consumer)):
#    @constructor()
    def __init__(self, callback_func):
        super().__init__()
        self.callback_func = callback_func

    @Override(jvoid, [Intent])
    def accept(self, t):
        print("Accept ran, with %s" % t)
        intent = cast(Intent, t)
        print("Accept action: %s" % intent.getAction())
        print("Accept describeContents: %s" % intent.describeContents())
        extraId = intent.getByteArrayExtra(NfcAdapter.EXTRA_ID)
        print("EXTRA_ID: %r" % extraId)
        print("ToString: %s" % intent.toString())
#        print("\n".join(dir(intent)))
        tag = intent.getParcelableExtra(NfcAdapter.EXTRA_TAG)
        print("Tag: %s" % tag)
        c = Calendar.getInstance()
        print("Accept calendar: %s" % c.getTime())
        self.callback_func(t)

def main():
    return BeeNFC_2()
