Ok, for this crackme, I am still trying to wrap my head around it as of today (20th October 2026), but I'll just freeze it here for now, what I have learnt from the crackme.

Opened crackme in IDA Free, searched for strings in it (View -> Open Subviews -> Strings)

![](Pasted%20image%2020261020103807.png)

Find the ones what have connection with the password check, double click that one to jump into the function that checks the password

![](Pasted%20image%2020261020104203.png)

then we take a look at the check, and we see that there are 3 checks, all chained together so that the user input must pass all 3 of them in oerder to get the success message. 

1. Length checker(input must == 14 characters)

![](Pasted%20image%2020261020105020.png)

2. SIMD(Single Instruction, Multiple Data ) check

![](Pasted%20image%2020261020105116.png)


![](Pasted%20image%2020261020105214.png)

3. Lastly, a scalar check

![](Pasted%20image%2020261020105621.png)


those are the 3 checks we have to reverse and generate a valid key for this binary. the good news is, the author probably wrote the binary with enough constraints in such a way that there's only a few viable candidates for the key. the bad news is, the author packed a truckload of intristics into the binary, that we need to decode later on.

[solver script](obsidian://open?vault=Writeups&file=scripts%2Fmy_first_crackme_solver.py)  I honestly don't know how the fuck this solver works, but I'll try to get to the bottom of this. by the time I finish, I'm probably halfway to the next Terrence Tao

