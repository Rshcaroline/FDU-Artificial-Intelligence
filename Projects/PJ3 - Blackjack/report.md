# Peeking Blackjack

> Author: Shihan Ran, 15307130424

## Problem 1: Value Iteration

### 1a. Question

Give the value of $V_{opt}(s)$ for each state $s$ after 0, 1, and 2 iterations of value iteration. Iteration 0 just initializes all the values of $V$ to 0. Terminal states do not have any optimal policies and take on a value of 0. 

### 1a. Answer

Recall the *value iteration* formula:
$$
V_{k+1}(s) \leftarrow \max_a \sum_{s'} T(s,a,s') [R(s,a,s')+\gamma V_k(s')]
$$

#### **Iteration 0**

Iteration 0 just initialize all the values of to 0:
$$
V_{0}(-2)=0\\
V_{0}(-1)=0\\
V_{0}(0)=0\\
V_{0}(1)=0\\
V_{0}(2)=0\\
$$

#### **Iteration 1**

Since Terminal states do not have any optimal policies and take on a value of 0, we have $V_{1}(-2)=0$ and $V_{1}(2)=0$. And $\gamma=1$. The process of iteration 1 is:
$$
\begin{aligned}
V_{1}(-1)&=\max_a \sum_{s'} T(-1,a,s') [R(-1,a,s')+ V_0(s')], \,\, a\in\{-1,+1\}\\
&=\max \{T(-1,-1,-2) [R(-1,-1,-2)+ V_0(-2)]+T(-1,-1,0) [R(-1,-1,0)+ V_0(0)],\\
&\cdots T(-1,+1,0) [R(-1,+1,0)+ V_0(0)]+T(-1,+1,-2) [R(-1,+1,-2)+ V_0(-2)]\}\\
&=\max \{0.8*(20+0)+0.2*(-5+0), 0.3*(-5+0)+0.7*(20+0)\}\\
&=15
\end{aligned}
$$
Similarly, we can get $V_2(0), V_2(1)​$. The final results are:
$$
\begin{aligned}
V_{1}(-2)&=0\\
V_{1}(-1)&=\max \{0.8*(20+0)+0.2*(-5+0), 0.3*(-5+0)+0.7*(20+0)\}=15 \\
V_{1}(0)&=\max \{0.8*(-5+0)+0.2*(-5+0), 0.3*(-5+0)+0.7*(-5+0)\}=-5 \\
V_{1}(1)&=\max \{0.8*(-5+0)+0.2*(100+0), 0.3*(100+0)+0.7*(-5+0)\}=26.5 \\
V_{1}(2)&=0\\
\end{aligned}
$$

#### **Iteration 2**

 The process of iteration 2 is:
$$
\begin{aligned}
V_{2}(-1)&=\max_a \sum_{s'} T(-1,a,s') [R(-1,a,s')+ V_1(s')], \,\, a\in\{-1,+1\}\\
&=\max \{T(-1,-1,-2) [R(-1,-1,-2)+ V_1(-2)]+T(-1,-1,0) [R(-1,-1,0)+ V_1(0)], \\
&\cdots T(-1,+1,0) [R(-1,+1,0)+ V_1(0)]+T(-1,+1,-2) [R(-1,+1,-2)+ V_1(-2)]\}\\
&=\max \{0.8*(20+0)+0.2*(-5-5), 0.3*(-5-5)+0.7*(20+0)\}\\
&=14
\end{aligned}
$$
Similarly, the final results are:
$$
\begin{aligned}
V_{2}(-2)&=0\\
V_{2}(-1)&=\max \{0.8*(20+0)+0.2*(-5-5), 0.3*(-5-5)+0.7*(20+0)\}=14\\
V_{2}(0)&=\max \{0.8*(-5+15)+0.2*(-5+26.5), 0.3*(-5+26.5)+0.7*(-5+15)\}=13.45\\
V_{2}(1)&=\max \{0.8*(-5-5)+0.2*(100+0), 0.3*(100+0)+0.7*(-5-5)\}=23\\
V_{2}(2)&=0\\
\end{aligned}
$$

### 1b. Question

What is the resulting optimal policy $\pi_{opt}$ for all non-terminal states? 

### 1b. Answer

After 7 iterations, it reaches convergence. $\pi_{opt}(-2)$ And $\pi_{opt}(2)$ are terminal states.

Other non-terminal states' optimal policy is $\pi_{opt}(-1)=-1$, $\pi_{opt}(0)=+1$, $\pi_{opt}(+1)=+1$.

## PROBLEM 2: TRANSFORMING MDPS

