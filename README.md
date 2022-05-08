# 原神角色资料语音

> 数据拉取自米游社-观测枢wiki

## 结构

`res` 目录中，`characterInfo.txt` 是观测枢角色语音相关页面的源码，从其中获取到每个角色对应的页面id（`get_id() in main.py`），`res/characterUrlDict.txt` 是获取到的角色与页面id，每行一个。



`res/csv` 目录中，是每个角色语音，在csv中保存为话题（topic）、文本（text）、语音url（audio）三列。



`res/audio` 目录中，按角色名称分文件夹保存的音频文件，共有3178个文件，占用449MB空间。



`src/main.py` 是用于抓取数据的爬虫源码。



## 声明

本仓库res目录中，角色名称、台词、语音音频版权属于米哈游（[上海米哈游网络科技股份有限公司](https://www.mihoyo.com/) / [HOYOVERSE](https://www.hoyoverse.com/)）； src目录中代码以[GPL-V3](https://www.gnu.org/licenses/gpl-3.0.html)许可证开源。

感谢原神制作组的精彩作品，也感谢米游社原神版块用户对于wiki数据整理的贡献。

本仓库仅供学习交流使用，使用数据进行商业用途需要版权方的授权。

如有侵权行为，可联系仓库管理员删除。