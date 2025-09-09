#!/usr/bin/osascript

on run
	set blogDraftPath to "/Users/magnusudbjorg/Documents/projects/magudb.github.io/_drafts/2025-08-31-Tech Digest: Fall 2025 Essential Reads for Tech Professionals.md"
	set shellScriptPath to POSIX path of (path to me as text)
	set shellScriptPath to replaceText(shellScriptPath, "add_to_blog.applescript", "append_link.sh")
	
	try
		-- Try to get info from Safari first
		tell application "System Events"
			set safariRunning to (name of processes) contains "Safari"
		end tell
		
		if safariRunning then
			tell application "Safari"
				if (count of windows) > 0 then
					set pageURL to URL of current tab of front window
					set pageTitle to name of current tab of front window
					
					-- Check if there's selected text
					set selectedText to ""
					try
						set selectedText to (do JavaScript "window.getSelection().toString()" in current tab of front window)
					end try
					
					if selectedText is not "" then
						set linkText to selectedText
					else
						set linkText to pageTitle
					end if
					
					-- Format the link in Jekyll/Markdown style
					set formattedLink to "- [" & linkText & "](" & pageURL & "){:target=\"_blank\"}"
					
					-- Call shell script to append the link
					do shell script "bash " & quoted form of shellScriptPath & " " & quoted form of blogDraftPath & " " & quoted form of formattedLink & " " & quoted form of pageURL
					
					display notification "Link added to blog draft" with title "Blog Link Added"
					return
				end if
			end tell
		end if
		
		-- Try Chrome if Safari isn't running or has no windows
		tell application "System Events"
			set chromeRunning to (name of processes) contains "Google Chrome"
		end tell
		
		if chromeRunning then
			tell application "Google Chrome"
				if (count of windows) > 0 then
					set pageURL to URL of active tab of front window
					set pageTitle to title of active tab of front window
					
					-- Check if there's selected text
					set selectedText to ""
					try
						set selectedText to execute active tab of front window javascript "window.getSelection().toString()"
					end try
					
					if selectedText is not "" then
						set linkText to selectedText
					else
						set linkText to pageTitle
					end if
					
					-- Format the link in Jekyll/Markdown style
					set formattedLink to "- [" & linkText & "](" & pageURL & "){:target=\"_blank\"}"
					
					-- Call shell script to append the link
					do shell script "bash " & quoted form of shellScriptPath & " " & quoted form of blogDraftPath & " " & quoted form of formattedLink & " " & quoted form of pageURL
					
					display notification "Link added to blog draft" with title "Blog Link Added"
					return
				end if
			end tell
		end if
		
		-- Try Microsoft Edge if Chrome isn't running or has no windows
		tell application "System Events"
			set edgeRunning to (name of processes) contains "Microsoft Edge"
		end tell
		
		if edgeRunning then
			tell application "Microsoft Edge"
				if (count of windows) > 0 then
					set pageURL to URL of active tab of front window
					set pageTitle to title of active tab of front window
					
					-- Check if there's selected text
					set selectedText to ""
					try
						set selectedText to execute active tab of front window javascript "window.getSelection().toString()"
					end try
					
					if selectedText is not "" then
						set linkText to selectedText
					else
						set linkText to pageTitle
					end if
					
					-- Format the link in Jekyll/Markdown style
					set formattedLink to "- [" & linkText & "](" & pageURL & "){:target=\"_blank\"}"
					
					-- Call shell script to append the link
					do shell script "bash " & quoted form of shellScriptPath & " " & quoted form of blogDraftPath & " " & quoted form of formattedLink & " " & quoted form of pageURL
					
					display notification "Link added to blog draft" with title "Blog Link Added"
					return
				end if
			end tell
		end if
		
		display alert "No browser window found" message "Please open Safari, Chrome, Edge with the page you want to add."
		
	on error errMsg
		display alert "Error" message errMsg
	end try
end run

on replaceText(theText, searchString, replacementString)
	set AppleScript's text item delimiters to searchString
	set theTextItems to every text item of theText
	set AppleScript's text item delimiters to replacementString
	set theText to theTextItems as string
	set AppleScript's text item delimiters to ""
	return theText
end replaceText
