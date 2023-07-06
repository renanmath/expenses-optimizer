# About the problem
We have a portfolio of possible future expenses, denoted by $\mathbb{E} = \{E_1,\dots, E_N\}$.  Each expense $E_i$ is a data consisted of the following information:
* a due date $d_i$ (in terms of days after starting day);
* a priority $p_i \in [1,3]$;
* a minimum cost value $\underline{g}_{i}$;
* a maximum cost value $\overline{g}_{i}$;
* a target cost value $\hat{g}_{i}$;
* a binary flag, $f_i$, indicating whether the expense is mandatory or not.

We also have the following relevant information:
* a recurrent expected budget $b$;
* a expected recurrence to the budget, $\delta$, in days;
* number of days since last recurrence $\delta_0$;
* a initial budget $b_0$;
* number of iterations $M$;

Note that the  due date and minimum and maximum cost information are optional. The priority is in descending order, that is, priority 1 is the highest priority. Obviously, mandatory expense has even higher priority. We also ask to $\underline{g}_{i} \le \hat{g}_{i} \le \overline{g}_{i}$. 
Usually, a monthly recurrence is expected, thus $\delta = 30$ in most cases.



# MILP Model
## Decision variables

We have the following decision variables:
* $x_{i,j}$: partial spend relative to $E_i$ in iteration $j$;
* $y_i$: binary variable, indicating wheater $E_i$ is going to be attended or not.
* $\epsilon_i$: absolute error between total spend on $E_i$ and target cost.

## Constraints

Total spend can not exceed maximum cost:

$$
\begin{align}
\sum_{j=0}^M x_{i,j}  \le y_i \cdot \overline{g}_i
\end{align}
$$

Minumum cost must be respected:
$$
\begin{align}
\sum_{j=0}^M x_{i,j}  \ge y_i \cdot \underline{g}_i
\end{align}
$$


One can not have partial spends after due date:

$$
\begin{align*}
x_{i,j} = 0 \,\,\, \textit{se } \, d_i < \delta - \delta_0 + (j-1) \cdot \delta
\end{align*}
$$

Total spends must respect budget in each iteration:

$$
\begin{align}
\sum_{i=1}^N \sum_{j=0}^k x_{i,j} \le b_0 + k \cdot b \,\,\, \forall \, k = 0,1,\dots, M
\end{align}
$$

Next constraint define relative error:
$$
\begin{align}
-\epsilon_i \cdot \hat{g}_i \le \sum_{j=0}^M x_{i,j} - \hat{g}_i \le \epsilon_i \cdot \hat{g}_i
\end{align}
$$


All mandatory expenses must be attendend:
$$
\begin{align}
y_i \ge f_i
\end{align}
$$

## Objective function

$$
\begin{align}
\textit{min} \sum_{i=0}^{M-1} \left( \frac{\epsilon_i}{p_i^C} + A \cdot y_i  \right)
\end{align}
$$

where $A \ge 0$ and  $C > 1$ are hyper-parameters.

 