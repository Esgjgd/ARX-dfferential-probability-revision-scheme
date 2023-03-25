# 基于多比特约束的ARX密码差分概率修正方案
# Differential probability revision scheme of ARX ciphers based on multi-bit constraints
This repository provides the supplementary code and data to the paper entitled "Differential probability revision scheme of ARX ciphers based on multi-bit constraints".
## Tested configuration
* Ubuntu18
* python 3.6
* pandas 1.4.4
* [cadical 1.5.3](https://github.com/arminbiere/cadical)
* [ARX Toolkit](https://who.rocq.inria.fr/Gaetan.Leurent/arxtools.html)
### 1.py
* to search paths.
### 2.py
* to output paths.
### pathtool2
* to run arxtoolkit automatically without interface.
* remember to put it into folder "arxtoolkit\arxtools\".
### paths.rar
* differential characteristics of 10-round SPECK32 differential (2800, 0010→0004, 0014) whose probability is over 2^(-50).
### r8.path、r8、r8KeyGen.path、r8KeyGen
* multi-bit constraints analysis of an 8-round SPECK32 differential characteristic and its key generation step.
* and results.
### pr_--.path、pr_all.path
* a script to see conditions under which 2.5-bit constraints are compatible.
* under "---" and under "???"
### else
* our algorithm and results.
