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


those are the 3 checks we have to reverve and generate a valid key for