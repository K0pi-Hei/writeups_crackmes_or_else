
challenge description:

a key checker that takes user input and then compares it to the stored password and tells us whether they key is correct or not. objectives are:

1. to find the correct key that is stored in the program,
2. and try to bypass the check altogether

So, let's see what we have here.

running DiE on the file, we get:


![[Pasted image 20261003231418.png]]


so, we now know that:

1. written in C or C++
2. has debugging data, which means that the function names are not stripped, which means that it will probably be a lot faster for the analysis process later.
3. and has visible strings, which is gonna be JACKPOT for a password checker like this, since it is usually stored as plain text for things like this.

Now, let's run 'strings' on this, and pipe it into a .txt file:


![[Pasted image 20261003232508.png]]


'strings' basically means to extract any plain text that the program has, which may have clues as to what the passwords are and what functions the program has. opening 'zexor_strings.txt', we CTRL+F for keywords like 'key', 'check', 'licence' and other such words that are prevalent in a password checker. we can see an interesting section of strings when we searched for 'key':

![[Pasted image 20261003234347.png]]

see that weird blob of text with stuff like 'Enter Licence Key' and 'Check Licence'? that might have just been pulled from the meat of the program, where all the juicy stuff are, which means that the password might just be near it. and the most promising candidate is the combination of words and letters 'AEXORRBSHA36325S33', so we will KIV that. Now we will move on to static analysis.

Load up Ghidra, the NSA reverser tool that is open-source, then we import the file into it, and the we import the file into it, and do auto-analysis. We, of course, search the 'main' function for clues, since it is a C/C++ program.

![[Pasted image 20261004000850.png]]

The first half of the function has nothing interesting much, just basic error handling and boilerplate.

![[Pasted image 20261004001227.png]]

Ok, the second half is a bit more interesting. see the highlighted 'WinMain'? in .exe files, that is the starting point function for GUI-based programs, so it would be interesting to see what is in there. double-click the highlighted, and we go into the 'WinMain' function.

![[Pasted image 20261004003737.png]]


Now, here's the WinMain function, and we can already see that there's something here. there's something called 'WndProc'.

WndProc, according to [learn.microsoft.com](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nc-winuser-wndproc) is :

"A callback function, which you define in your application, that processes messages sent to a window. The **WNDPROC** type defines a pointer to this callback function. The _WndProc_ name is a placeholder for the name of the function that you define in your application."

to TL;DR for illiterate peasants like us, it basically means where our input goes to be processed after we click 'Check' after entering the input. so that is probably our next function to look into. double-click and we jump.

![[Pasted image 20261004010506.png]]

And yes!! we found the REAL main function, where the action happens, and we can see that there is a very suspicious function labelled as 'CheckLicense', which we will be looking at now. Jumping to 'CheckLicense':

![[Pasted image 20261004011006.png]]

The heart of the CheckLicense function is pretty simple: it uses strcmp to compare between param_1, which is a user input, and some pointer called 'PTR_s_AEXORRBSHA36325S33_140003000'. that means that the real password is stored somewhere that is pointed by the pointer. Now we find where it is stored in the memory by opening the 'listing' window, and then we click on the PTR. 

![[Pasted image 20261004011715.png]]

now, we see that 'PTR_s_AEXORRBSHA36325S33_140003000' points to 'AEXORRBSHA36325S33_140004000', which points to a string (actually it's an array, but we'll let it slide) of bytes that is plaintext "AEXORRBSHA36325S33", making us 99% sure that is is the password. also, it is XREF (referenced) to the LicenseCheck function, meaning that it is used in that function.

Let's check if our hypothesis is true by starting up that program and using AEXORRBSHA36325S33 as the key....

![[Pasted image 20261004012725.png]]


AND YESS!!! IT IS CORRECT!! Now we know that the password is stored in the memory in plaintext form all along, which is a very idiotic move in the situation where we have to build a real licence key checker, but in this scenario, it is perfect for the crackme. Objective one done, we shall continue tomorrow morning

Ok,