#!/usr/bin/osascript

on run
    set scriptPath to (path to me as text)
    set AppleScript's text item delimiters to ":"
    set pathItems to text items of scriptPath
    set pathItems to items 1 thru -2 of pathItems
    set AppleScript's text item delimiters to ":"
    set scriptDir to pathItems as text
    set pythonScript to scriptDir & ":add_link.py"
    
    set pythonScriptPOSIX to POSIX path of pythonScript
    
    -- Initialize variables
    set pageURL to ""
    set pageTitle to ""
    set selectedText to ""
    
    -- Try different browsers in order
    if application "Safari" is running then
        try
            tell application "Safari"
                set pageURL to URL of current tab of front window
                set pageTitle to name of current tab of front window
                set selectedText to (do JavaScript "window.getSelection().toString()" in current tab of front window)
            end tell
        on error
            -- Safari failed, try next browser
        end try
    end if
    
    if pageURL is "" and application "Google Chrome" is running then
        try
            tell application "Google Chrome"
                set pageURL to URL of active tab of front window
                set pageTitle to title of active tab of front window
                set selectedText to execute front window's active tab javascript "window.getSelection().toString()"
            end tell
        on error
            -- Chrome failed, try next browser
        end try
    end if
    
    if pageURL is "" and application "Microsoft Edge" is running then
        try
            tell application "Microsoft Edge"
                set pageURL to URL of active tab of front window
                set pageTitle to title of active tab of front window
                set selectedText to execute front window's active tab javascript "window.getSelection().toString()"
            end tell
        on error
            -- Edge failed, try next browser
        end try
    end if
    
    if pageURL is "" and application "Firefox" is running then
        -- Firefox requires different approach
        tell application "System Events"
            tell process "Firefox"
                set frontmost to true
                -- Get URL from address bar
                keystroke "l" using {command down}
                delay 0.1
                keystroke "c" using {command down}
                delay 0.1
            end tell
        end tell
        set pageURL to the clipboard
        
        -- Get title from window name
        tell application "Firefox"
            set pageTitle to name of front window
        end tell
        
        -- Can't get selected text from Firefox easily
        set selectedText to ""
    end if
    
    if pageURL is "" then
        display notification "No supported browser found or couldn't get URL" with title "Error"
        return
    end if
    
    -- Clean up title if it ends with browser name
    if pageTitle ends with " - Safari" then
        set pageTitle to text 1 thru -10 of pageTitle
    else if pageTitle ends with " - Google Chrome" then
        set pageTitle to text 1 thru -17 of pageTitle
    else if pageTitle ends with " — Mozilla Firefox" then
        set pageTitle to text 1 thru -19 of pageTitle
    else if pageTitle ends with " - Microsoft Edge" then
        set pageTitle to text 1 thru -18 of pageTitle
    end if
    
    -- Build command
    set pythonCmd to "python3 " & quoted form of pythonScriptPOSIX & " --browser"
    set pythonCmd to pythonCmd & " --url " & quoted form of pageURL
    set pythonCmd to pythonCmd & " --title " & quoted form of pageTitle
    
    if selectedText is not "" then
        set pythonCmd to pythonCmd & " --selected " & quoted form of selectedText
    end if
    
    -- Execute Python script with error handling
    try
        set shellResult to do shell script pythonCmd
        -- If we get here, the command succeeded
    on error errMsg number errNum
        -- Log error to file
        set logFile to scriptDir & ":add_link_errors.log"
        set logFilePOSIX to POSIX path of logFile
        set timestamp to do shell script "date '+%Y-%m-%d %H:%M:%S'"
        set errorLog to "\n" & "=" & "=" & "=" & "=" & "=" & "=" & "=" & "=" & "=" & "=" & "\n"
        set errorLog to errorLog & "AppleScript Error at " & timestamp & "\n"
        set errorLog to errorLog & "Error: " & errMsg & " (" & errNum & ")\n"
        set errorLog to errorLog & "Command: " & pythonCmd & "\n"
        set errorLog to errorLog & "URL: " & pageURL & "\n"
        set errorLog to errorLog & "Title: " & pageTitle & "\n"
        set errorLog to errorLog & "=" & "=" & "=" & "=" & "=" & "=" & "=" & "=" & "=" & "=" & "\n"
        
        do shell script "echo " & quoted form of errorLog & " >> " & quoted form of logFilePOSIX
        
        display notification "Error adding link. Check add_link_errors.log" with title "Link Add Error"
        return
    end try
end run