---
layout: post
title: Solving some Project Euler problems
#subtitle: Or, how I made this blog
#gh-repo: oena/oena.github.io
#gh-badge: [star, fork, follow]
tags: [python, Project Euler, statistics]
comments: false
readtime: true
---

I recently solved three [Project Euler](https://projecteuler.net/) problems: one solved by fewer than 500,000 people ("Problem 1"), one solved by fewer than 100,000 people ("Problem 2"), and one solved by fewer than 25,000 people ("Problem 3). You can find my code for my solutions [here](https://github.com/oena/oena.github.io/blob/master/ipynbs/Project_Euler_Problems.ipynb); in this post, I'll just explain my reasoning behind the approach I took. 

## Problem 1 (Actually Problem 7 in Project Euler) 

### The problem

By listing the first six prime numbers: 2, 3, 5, 7, 11, and 13, we can see that the 6th prime is 13. What is the 10,001st prime number?

### My approach

My first thought regarding this problem is that it required two things: (1) a way to generate prime numbers and (2) A way to get the nth prime number. 

1. **A way to generate prime numbers**: Since this problem involves a large number of values, I decided from the start that using a [generator](https://wiki.python.org/moin/Generators) would probably be an efficient approach because they load values on demand and you can use them before generating all values. My first thought was to iterate (after 2, the only even prime number) through the odd numbers, checking if each value was divisible by any of the prior primes. I do think such a solution could work, but mine ended up being slightly ~fancier~ because I vaguely remembered there being some rule about figuring out if a number was prime, and found [the trial division algorithm](https://www.khanacademy.org/computing/computer-science/cryptography/comp-number-theory/a/trial-division), which says that if we don't find a divisor of a number n after checking up to the square root of n, then n must be prime. So, in the end I wrote a function to make a generator of prime values (which is slightly more efficient than it would be otherwise thanks to the trial division algorithm). 

2. **A way to get the nth prime number**: Once my generator was done, writing a function to get the nth prime was pretty easy. Basically, I enumerated through the values of my prime generator until I got to n. `enumerate` is a handy method to use here because it keeps count for you as it goes through an iterator/generator, so I used it to tell me when I got to n. 

**Solution**: The 10,001th prime is 104,743. 

## Problem 2 (Actually Problem 34 in Project Euler) 


### The problem

145 is a curious number, as 1! + 4! + 5! = 1 + 24 + 120 = 145. Find the sum of all numbers which are equal to the sum of the factorial of their digits. Note: As 1! = 1 and 2! = 2 are not sums they are not included.

### My approach

I was helped in my solution to this problem a lot by googling; specifically, I wondered if there was a term for numbers that are equal to the sum of their digits and it turns out that there is-- these are called **factorions**, and links from [the Wikipedia page for factorions](https://en.wikipedia.org/wiki/Factorion) is especially helpful for this problem. 

Otherwise, this problem also required two things: (1) a way to get the sum of the factorials of a given number's digits (2) A way to get the sum of all factorions. 

1. **A way to get the sum of the factorials of a given number's digits**: This was the easy part. I remembered that it was pretty easy to iterate over characters of a string, so I split my number (call it `m`) into digits using this feature of strings and a list comprehension. Then, the `factorial` method in the math library (along with a second list comprehension, and the sum of this second list) got me the rest of the way there.  
2. **A way to get the sum of all factorions**: With a way to calculate the sum of the factorials of a given number's digits, identifying a single factorion is pretty simple; you just check if the number is equal to this sum. But, I wasn't initially sure how to know when to *stop* trying numbers. Luckily for me, I found an answer via the Wikipedia page: 

    > If n is a natural number of d digits that is a factorion, then 10d − 1 ≤ n ≤ 9!d. 
    > This fails to hold for d ≥ 8 thus n has at most 7 digits, and the first upper bound is 9,999,999. 
    > But the maximum sum of factorials of digits for a 7 digit number is 9!*7 = 2,540,160 establishing the second upper bound.

    > All factorials of digits at least 5 have the factors 5 and 2 and thus end on 0. Let 1abcdef denote our 7 digit number. 
    > If all digits a-f are all at least 5, the sum of the factorials – which is supposed to be equal to 1abcdef – 
    > will end on 1 (coming from the 1! in the beginning).

    > This is a contradiction to the assumption that f is at least 5. Thus, at least one of the digits a-f can be at most 4, 
    > which   establishes 1!+4!+5*9!=1814425 as fifth upper bound. Assuming n is a 7 digit number, the second digit is at most 8. 
    > There are two cases: If a is at least 5, by the same argument as above one of the remaining digits b-f has to be at most 4. 
    > This implies an upper bound (since a is at most 8) of 1!+8!+4!+4*9!= 1491865, a contradiction to a being at least 5. 
    > Thus, a is at most 4 and the sixth upper bound is 1499999.
  
  TLDR: An upper bound for factorions is 1,499,999; for simplicity, I used 1,500,000 in my code. The lower bound for a factorion is 10, because (knowing factorials a little) none of the single digits are equal to their factorials. 
  
  From here, I found all factorions between my lower and upper bounds using a list comprehension, and took a sum of the list. 

**Solution**: 40,730. 

**Note.** The time for this could likely be improved further by caching the values of single digit factorials, because you use those over and over again. But I didn't have time to look into it, and on the whole I prioritized getting the right answer over optimal speed/efficiency. 

## Problem 3 (Actually Problem 493 in Project Euler) 

To be honest I chose this problem because I liked the name ("Under the Rainbow"), and (after reading it) I liked that it was really a statistics problem. I was a little surprised that so few (4778 last I checked) people had solved this problem, but I guess most people don't scroll that far/like statistics :) 

### The problem

70 coloured balls are placed in an urn, 10 for each of the seven rainbow colours. What is the expected number of distinct colours in 20 randomly picked balls? Give your answer with nine digits after the decimal point (a.bcdefghij).

### My approach

This problem is pretty straightforward if you know about [linearity of expectation](https://www.geeksforgeeks.org/linearity-of-expectation/) and a little probability. 

First, for one color, the probability that it's chosen at least once, Pr(ball of color c is chosen at least once) = 1 - Pr(ball of color c is never chosen). For the setup here, this equals 1 - (60 choose 20)/(70 choose 20). 

Then, for 7 colors, the expectation is the product of 7 times the expectation for a single color (or, 7 times the probability that one color is chosen at least once). And that's it! 

**Solution (rounded to 9 decimal places as per instructions)**: 6.818741802
