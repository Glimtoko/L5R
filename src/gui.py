import wx
import wx.richtext

from proxy import create_proxy_pdf, load_cards

class L5RProxy(wx.Frame):
    def __init__( self, parent ):
        wx.Frame.__init__(
            self,
            parent,
            id = wx.ID_ANY,
            title = wx.EmptyString,
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


        self.SetSizer( bSizer1 )
        self.Layout()

        self.Centre( wx.BOTH )

    def on_file_changed(self, event):
        file_path = self.m_filePicker1.GetPath()
        self.m_richText1.Clear()
        try:
            with open(file_path, 'r') as file:
                content = file.read()
                self.m_richText1.WriteText(content)
        except Exception as e:
            self.m_richText1.WriteText(f"Error reading file: {e}")

    def on_button_click(self, event):
        text = self.m_richText1.GetValue()
        cards = load_cards(text.splitlines())
        output_path = self.m_filePicker1.GetPath()
        if output_path == "":
            output_path = "output.pdf"
        else:
            output_path = output_path.rsplit('.', 1)[0] + ".pdf"  # Change extension to .pdf
        result = create_proxy_pdf(cards, output_path)

    def __del__( self ):
        pass


def do_gui():
    app = wx.App(False)
    frame = L5RProxy(None)
    frame.Show(True)
    app.MainLoop()


if __name__ == "__main__":
    do_gui()
