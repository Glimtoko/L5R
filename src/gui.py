import wx
import wx.richtext

from proxy import create_proxy_pdf, load_cards
from validate import validate_deck

class L5RProxy(wx.Frame):
    def __init__( self, parent ):
        """Create a new L5RProxy frame with a file picker, rich text control, radio box for database selection, and
        buttons for creating proxies."""

        wx.Frame.__init__(
            self,
            parent,
            id = wx.ID_ANY,
            title = "L5R Proxy Generator",
            pos = wx.DefaultPosition,
            size = wx.Size( 815,576 ),
            style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL
        )

        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )

        bSizer1 = wx.BoxSizer( wx.VERTICAL )

        self.m_filePicker1 = wx.FilePickerCtrl(
            self,
            wx.ID_ANY,
            wx.EmptyString,
            u"Select a file",
            u"*.*",
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.FLP_DEFAULT_STYLE
        )
        self.m_filePicker1.Bind(wx.EVT_FILEPICKER_CHANGED, self.on_file_changed)
        bSizer1.Add( self.m_filePicker1, 0, wx.ALL, 5 )

        self.m_richText1 = wx.richtext.RichTextCtrl(
            self,
            wx.ID_ANY,
            wx.EmptyString,
            wx.DefaultPosition,
            wx.DefaultSize,
            0|wx.VSCROLL|wx.HSCROLL|wx.NO_BORDER|wx.WANTS_CHARS
        )
        bSizer1.Add( self.m_richText1, 1, wx.EXPAND |wx.ALL, 5 )

        self.m_ignoreErrorsCheckBox = wx.CheckBox(
            self,
            wx.ID_ANY,
            u"Ignore Validation Errors",
            wx.DefaultPosition,
            wx.DefaultSize,
            0
        )
        # self.m_ignoreErrorsCheckBox.SetValue(True)
        bSizer1.Add( self.m_ignoreErrorsCheckBox, 0, wx.ALL, 5 )

        self.m_button1 = wx.Button(
            self,
            wx.ID_ANY,
            u"Create Proxies",
            wx.DefaultPosition,
            wx.DefaultSize,
            0
        )
        self.m_button1.Bind(wx.EVT_BUTTON, self.on_button_click)
        bSizer1.Add( self.m_button1, 0, wx.ALL, 5 )

        self.m_messages = wx.TextCtrl(
            self,
            wx.ID_ANY,
            wx.EmptyString,
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.TE_MULTILINE|wx.TE_READONLY
        )
        bSizer1.Add( self.m_messages, 1, wx.EXPAND |wx.ALL, 5 )

        self.SetSizer( bSizer1 )
        self.Layout()

        self.Centre( wx.BOTH )

    def on_file_changed(self, event):
        """Handle the file picker change event by reading the selected file and displaying its
        contents in the rich text control."""

        file_path = self.m_filePicker1.GetPath()
        self.m_richText1.Clear()
        try:
            with open(file_path, 'r') as file:
                content = file.read()
                self.m_richText1.WriteText(content)
        except Exception as e:
            self.m_messages.WriteText(f"Error reading file: {e}")

    def on_button_click(self, event):
        """Handle the button click event by loading cards from the rich text control, validating them, and creating a
        proxy PDF if there are no validation errors or if the user has chosen to ignore them."""
        self.m_messages.Clear()
        text = self.m_richText1.GetValue()
        cards = load_cards(text.splitlines(), text_ctrl_object=self.m_messages)
        if cards is not None:
            output_path = self.m_filePicker1.GetPath()
            if output_path == "":
                output_path = "output.pdf"
            else:
                output_path = output_path.rsplit('.', 1)[0] + ".pdf"  # Change extension to .pdf

            ignore_errors = self.m_ignoreErrorsCheckBox.GetValue()
            valid = validate_deck(cards, text_ctrl_object=self.m_messages)
            if valid or ignore_errors:
                result = create_proxy_pdf(cards, output_path, text_ctrl_object=self.m_messages)
        else:
            self.m_messages.WriteText("Error: Invalid card names in input text.\n")

    def __del__( self ):
        pass


def do_gui():
    app = wx.App(False)
    frame = L5RProxy(None)
    frame.Show(True)
    app.MainLoop()


if __name__ == "__main__":
    try:
        import pyi_splash
    except ImportError:
        pass
    else:
        pyi_splash.close()

    do_gui()
