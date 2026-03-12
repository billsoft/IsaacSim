---
trigger: always_on
---
当前是win11系统,注意windows和linux的命令有一些差异,而且命令行工具也不同，如果是windows命令行powershell请注意命令格式
conda activate isaac 是我们的python环境名称,执行任何python相关命令前都需要先激活这个环境,不要在base环境下按照包部署环境，如果必须请提示确认。

运行各种命令安装包是记得我的python版本是3.12 但大多数isaac包是3.11的
但是isaac sim和lab好像有自己的本地python环境,不依赖conda环境和系统python,在 D:\code\IsaacSim\_repo\python 请根据具体情况是运行isaac的内容使用这个

vs2022 C:\Program Files\Microsoft Visual Studio\2022\Professional 和vs2026  C:\Program Files\Microsoft Visual Studio\18\Professional 我都有安装
