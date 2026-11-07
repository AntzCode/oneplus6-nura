Title: Text typed by another client lands before the preedit word; no way to commit it

Date: 20261021

Summary

With completion on (completion-mode ['hint']), Stevia holds the word being typed as preedit. Text that another client sends through the virtual-keyboard protocol (e.g. wtype) is inserted at the app's real cursor, which is at the start of the preedit. So it lands before the word, and the word stays underlined after it.

Only a tap in the text commits the word. There's no way for another program to make Stevia commit its preedit first.

Steps to reproduce

1. Open a GTK 4 text field (e.g. GNOME Text Editor) with completion on (completion-mode ['hint']).
2. Type hello with Stevia, so it's underlined as preedit.
3. From another client, type a character through the virtual-keyboard protocol: wtype ©

Expected: hello©, with the caret after ©.

Actual: ©hello. hello is still underlined preedit, and the caret is between them.

Use case

I'm writing og-home-panel, a bar with Back, an app switcher and quick actions for Phosh. One row has buttons that type hard-to-find characters (macrons, currency signs, ©, °, Ω …) with wtype. While a word is in preedit, every one of them lands in front of it.

What I tried (none commit the preedit)

- Hiding and reshowing the OSK (sm.puri.OSK0.SetVisible false, wait 150 ms, type, SetVisible true): the text still lands before the word, which stays underlined.
- Left then Right before the text: the preedit word is dropped, and the text replaces it.
- Space, then BackSpace before the text (with and without 150 ms gaps): inconsistent. The text either lands before the word or replaces it.
- Space, wait 150 ms, then the text:  ©hello, with hello still underlined.
- Setting completion-mode to [] for 150 ms around the typing: no change to the current preedit.

Turning completion off works around it, but a

Request

A way for another client to have Stevia commidit, for example:

- a method on sm.puri.OSK0 (e.g. CommitPreedi
- committing the preedit when a key event from another client's virtual keyboard arrives for the same text input.

Then tools that type text (panels, wtype, dictation, text expanders) could work alongside completion.

Versions

- postmarketOS v26.06 (Nura), OnePlus 6
- stevia 0.55.0, phosh 0.55.0, phoc 0.55.1
- GTK 4.22.4, wtype 0.4
