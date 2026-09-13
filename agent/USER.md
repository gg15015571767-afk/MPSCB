# User Profile

本系统面向**多终端用户**（飞书等 IM 平台的客户），无单一用户画像。

个性化信息（称呼、语言等）由 `set_user_preference` 按 `user_id` 维度记录，存于 PreferenceStore（见 `../技术文档.md` §11.9），不在此处维护。
