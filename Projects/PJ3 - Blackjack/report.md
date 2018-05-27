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

### 2a. Check my Code.

### 2b. Question

Suppose we have an acyclic MDP (you will not visit a state a second time in this process). We could run value iteration, which would require multiple iterations. Briefly explain a more efficient algorithm that only requires one pass over all the triples. 

### ==2b. Answer==

### 2c. Question

Suppose we have an MDP with states a discount factor $\gamma<1$, but we have an MDP solver that only can solve MDPs with discount 1. How can leverage the MDP solver to solve the original MDP? 

### 2c. Answer

$$
\begin{aligned}
T'(s,a,s')&=\gamma T(s,a,s'), \,\, s'\in States \\
T'(s,a,o)&=1-\gamma \sum_{s'} T(s,a,s')=1-\gamma\\
Reward'(s,a,s')&=\frac{1}{\gamma} Reward(s,a,s'),\,\, s'\in States \\
Reward'(s,a,o)&=0\\
\end{aligned}
$$

## PROBLEM 3: PEEKING BLACKJACK 

### 3a. Check my Code.

### 3b. Check my Code.

## PROBLEM 4: LEARNING TO PLAY BLACKJACK

### 4a. Check my Code.

### 4b. Question

Call *simulate()* using your algorithm and the *identityFeatureExtractor()* on the MDP *smallMDP*, with 30000 trials. Compare the policy learned in this case to the policy learned by value iteration. Don't forget to set the explorationProb of your Q-learning algorithm to 0 after learning the policy. How do the two policies compare (i.e., for how many states do they produce a different action)? Now run *simulate()* on *largeMDP*. How does the policy learned in this case compare to the policy learned by value iteration? What went wrong? 

### 4b. Answer

|                                              | Small MDP                                                    | Large MDP                                                    |
| -------------------------------------------- | :----------------------------------------------------------- | ------------------------------------------------------------ |
| Value Iteration                              | 5                                                            | 29                                                           |
| Intersection probabilitiy between 2 policies | 0.74                                                         | 0.61                                                         |
| Reasons                                      | Since the relatively small state space allows Q­learning algorithm to learn the Q values better, Q­learning does better than value iteration. | Since the state space is much lager, which make Q­learning algorithm not capable of learning accurate Q values. Also, our implemented *identityFeatureExtractor* can only return a singleton list containing indicator feature for the (state, action) pair and it provides no generalization. |

### 4c. Check my Code.

### 4d. Question

Now let's explore the way in which value iteration responds to a change in the rules of the MDP. Run value iteration on originalMDP to compute an optimal policy. Then apply your policy to newThresholdMDP by calling simulate with FixedRLAlgorithm, instantiated using your computed policy. What reward do you get? What happens if you run Q learning on newThresholdMDP instead? Explain. 

### 4d. Answer

I get relatively low sum rewards **205393** for FixedRLAlgorithm because I passed the policy learned for originalMDP in it. Since FixedRLAlgorithm can not adapt, the actions taken are not optimal actions for newThresholdMDP. 

Q­learning has higher sum rewards **360000** because it is able to adapt to newThresholdMDP. 