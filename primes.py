# primes.py

from sympy import isprime, primefactors

def generate_primes(n):
    primes = [num for num in range(2, n) if isprime(num)]
    return primes

def factorize_number(num):
    return primefactors(num)
