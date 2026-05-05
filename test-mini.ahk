#SingleInstance Force
#Requires AutoHotkey v2.0

; Ultra minimal version
gw := Gui("GW2Bard")
gw.Add("Text",, "Hello")
gw.Add("Button", "x10 y30 gPlay", "Play")
gw.Show()

Play() {
    MsgBox("Works!")
}