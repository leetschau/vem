# vem

vem: neovim environment manager

使用编译型语言生成不依赖外部环境的二进制文件。

vim 有3种工作环境：
. 基本文本编辑 base: 只有一些配置和快捷键，不需要安装插件；
. 高级文本编辑 text: 包含常用的编辑功能，如文本补全、注释、窗口最大化等；
. 语言开发环境 lang: 对指定语言通过插件提供专门支持；

根据不同环境要求生成包含 vam 插件定义的 vim 配置文件，
运行时通过 vam 安装插件，生成一个完全可用的 vim。

## API

* vem st base
* vem st text
* vem st lang <lang-list>, e.g.: vem st lang python-clojure-nim
* vem rb 回退到上次安装
* vem up 使用上次设置的等级，用新的 vem 文件生成新配置并安装

## 工作流程

### 参数设置

* profile 文件位置：prof_base, 默认值 ~/.local/vem

* vim 配置文件位置：prof_target, 默认值 ~/.config/nvim

### set/rollback

由于将所有配置整合成 init.vim 一个文件，省去了清理目录的操作。

set 流程：

1. 生成新配置文件 /tmp/init.vim（set, rollback, update 分别进行）
1. cp $prof_target/init.vim $prof_base/backup.vim
1. cp /tmp/init.vim $prof_target/init.vim

rollback 过程是将 set 第一步改为 `cp $prof_base/backup.vim /tmp/init.vim`
后续步骤不变。

update 就是读当前配置的 level 然后用它作参数调用 set 过程。

### 生成配置文件

生成的配置文件第一行中包含此次生成配置所执行的命令，
作为下次使用 `update` 命令更新时的参数。

* base: base.vem
* text: base.vim + text.vem
* langs: base.yml + text.yml + langs.yml,
  其中 langs.yml 由 langs 列表对应的 <lang>.yml 文件组合而成，
  例如当 langs = ['python', 'nim'] 时，langs.yml 由 python.yml
  和 nim.yml 组合而成。

### 管理插件

所有更新均不直接编辑 vim 配置文件，而是修改所属范围的 vem 文件，
然后用 `vem up` 更新到生产环境中。

## 项目文件结构

* app/: 包含 vem 源码

* profiles/: 包含 vim 配置组件，base.yml, text.yml 和不同语言的配置文件，
  例如 python.yml, nim.yml 等

## vem 文件结构

### 依赖插件版本（暂不实现）

vem 文件尽量使用 vim 语法和插件语法，
vem 工具只做简单的文件拼接和插件管理工具的安装，
以降低 vem 工具的实现复杂度和与 vim 插件管理工具的耦合。

<lang>.yml 包含配置和插件列表两部分，例如：
```
let g:clojure:something = 0

Plug 'guns/vim-clojure-highlight', { 'for': 'clojure' }
```

### 插件中立版本

vem 文件只记录配置和插件信息，与使用何种插件无关，
比如上面的例子使用了 vim-plug 语法，对等的 vam 语法为：
```
let g:clojure:something = 0

autocmd FileType clojure :VAMActivate github:guns/vim-clojure-highlight
```

使用 YAML 格式记录插件配置，
其中 conf 部分为 配置信息，
plugins 部分为插件列表。
