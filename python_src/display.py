import pygtk
import pango
import gtk

class display():
    def __init__(self):
        gtk.gdk.threads_init()
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.fullscreen()
        self.window.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse('#234fdb'))
        self.window.connect("delete-event", gtk.main_quit)
        self.window.connect("key_press_event", self.on_key_press)
        self.window.show()
        
        self.buffer = gtk.TextBuffer()
        self.buffer.set_text("Cake")
        
        self.text = gtk.TextView(self.buffer)
        self.text.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse('#234fdb'))
        self.text.modify_text(gtk.STATE_NORMAL, gtk.gdk.color_parse('#ffff00'))
        self.text.modify_font(pango.FontDescription('Helvetica 70'))
        self.text.set_justification(gtk.JUSTIFY_CENTER)
        self.text.set_editable(False)
        self.text.set_wrap_mode(gtk.WRAP_WORD)
        self.text.show()
        
        self.window.add(self.text)
        
    def __destroy(self):
        print "Here"
#        gtk.threads_enter()
        print "There"
        #self.window.unfullscreen()
        #self.window.hide()
        gtk.main_quit()
        print "Everywhere"
#        gtk.threads_leave()
    
    def on_key_press(self, widget, event):
        print "KEY! " + gtk.gdk.keyval_name(event.keyval)
        if gtk.gdk.keyval_name(event.keyval) == "Escape":
            self.__destroy()
    def update_text(self, text):
        gtk.threads_enter()
        self.buffer.set_text(text)
        gtk.threads_leave()

if __name__ == "__main__":
    from time import sleep
    import threading
    disp = display()
    def update_disp():
        i = 0
        lines = [
        	"Amazing grace, How sweet the sound\nThat saved a wretch like me.",
        	"I once was lost, but now am found,",
        	"Was blind, but now I see.",
        	"'Twas grace that taught my heart to fear,",
        	"And grace my fears relieved.",
        	"How precious did that grace appear",
        	"The hour I first believed.",
        	"Through many dangers, toils and snares",
        	"I have already come,",
        	"'Tis grace has brought me safe thus far",
        	"And grace will lead me home.",
        	"The Lord has promised good to me",
        	"His word my hope secures;",
        	"He will my shield and portion be,",
        	"As long as life endures.",
        	"Yea, when this flesh and heart shall fail,",
        	"And mortal life shall cease",
        	"I shall possess within the veil,",
        	"A life of joy and peace.",
        	"When we've been there ten thousand years",
        	"Bright shining as the sun,",
        	"We've no less days to sing God's praise",
        	"Than when we've first begun."]
        while True:
            disp.update_text(lines[i])
            if i == len(lines) - 1:
                i = 0
            else:
                i = i + 1
            sleep(1)
    thread = threading.Thread(target=update_disp)
    thread.daemon = True
    thread.start()
    gtk.main()
