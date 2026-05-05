#SingleInstance Force
#Requires AutoHotkey v2.0

; Simple test version 3 without SetFont
FileAppend("Start`n", A_ScriptDir . "\test.txt")

GW2_PROCESS := "Gw2-64.exe"
FileAppend("1`n", A_ScriptDir . "\test.txt")

SONG_FOLDER := A_ScriptDir . "\songs"
FileAppend("2`n", A_ScriptDir . "\test.txt")

KEYBINDINGS := Map("note1", "1", "note2", "2")
FileAppend("3`n", A_ScriptDir . "\test.txt")

MainGui := Gui("+Resize", "GW2Bard")
FileAppend("4`n", A_ScriptDir . "\test.txt")

; Removed SetFont - causes issues
FileAppend("5`n", A_ScriptDir . "\test.txt")

MainGui.Add("Text", "x10 y10", "GW2Bard")
FileAppend("6`n", A_ScriptDir . "\test.txt")

MainGui.Add("Button", "x10 y40 gPlay", "Play")
FileAppend("7`n", A_ScriptDir . "\test.txt")

lb := MainGui.Add("ListBox", "x10 y80 w250 h150")
FileAppend("8`n", A_ScriptDir . "\test.txt")

MainGui.Show()
FileAppend("9`n", A_ScriptDir . "\test.txt")

Folder := SONG_FOLDER . "\harp"
if !DirExist(Folder)
    DirCreate(Folder)

lb.Delete()
FileAppend("10`n", A_ScriptDir . "\test.txt")

Loop Files, Folder . "\*.json" {
    lb.Add(StrReplace(A_LoopFileName, ".json"))
}
FileAppend("11`n", A_ScriptDir . "\test.txt")

Hotkey("F9", "Play")
Hotkey("Esc", "Stop")
FileAppend("DONE`n", A_ScriptDir . "\test.txt")

Play() {
    FileAppend("Play`n", A_ScriptDir . "\test.txt")
}

Stop() {
    FileAppend("Stop`n", A_ScriptDir . "\test.txt")
}