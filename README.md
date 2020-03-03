# vem

vem: vim environment manager

Generate vim configuration files in the following environments:

* Basic text editing profile *base*: only some vim built-in
  configurations and keyboard mappings, no plugins.

* Advanced text editing profile *text*:
  based on *base* profile, adding more functions with plugins
  such as auto-completion, toggle comments, maximize window, etc.

* Developing profile *langs*: based on previous 2 profiles,
  plus plugins for  for specific languages, such as Python,
  Haskell, etc. Turn vim in IDE-like tools.

Only for Linux and neovim by now, while easy to make it compatible
with vim and Windows.

## Installation

Build from source:
```
git clone https://github.com/leetschau/vem.git
cd vem
. env/bin/activate
pyinstaller -F vem.py
```

Or download binary `vem` and *profile* folder to local host.

## Usage

`./vem --prof-base=profiles st text`.

Run `./vem` for help.

# Develop

使用编译型语言生成不依赖外部环境的二进制文件。

## API

* vem st base
* vem st text
* vem st lang <lang-list>, e.g.: vem st lang python-clojure-nim
* vem rb 回退到上次安装
* vem up 使用上次设置的等级，用新的 vem 文件生成新配置并安装

## Workflow

### Parameter setup

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

### How to build vim profile

生成的配置文件第一行中包含此次生成配置所执行的命令，
作为下次使用 `update` 命令更新时的参数。

* base: base.yml
* text: base.yml + text.yml
* langs: base.yml + text.yml + langs.yml,
  其中 langs.yml 由 langs 列表对应的 <lang>.yml 文件组合而成，
  例如当 langs = ['python', 'nim'] 时，langs.yml 由 python.yml
  和 nim.yml 组合而成。

### Manage plugins

所有更新均不直接编辑 vim 配置文件，而是修改所属范围的 vem 文件，
然后用 `vem up` 更新到生产环境中。

## Project structure

* app/: 包含 vem 源码

* profiles/: 包含 vim 配置组件，base.yml, text.yml 和不同语言的配置文件，
  例如 python.yml, nim.yml 等

## File structure of a profile

### vim-plug specific version (deprecated)

vem 文件尽量使用 vim 语法和插件语法，
vem 工具只做简单的文件拼接和插件管理工具的安装，
以降低 vem 工具的实现复杂度和与 vim 插件管理工具的耦合。

<lang>.yml 包含配置和插件列表两部分，例如：
```
let g:clojure:something = 0

Plug 'guns/vim-clojure-highlight', { 'for': 'clojure' }
```

### Plugin manager agnostic style

vem 文件只记录配置和插件信息，与使用何种插件无关，
比如上面的例子使用了 vim-plug 语法，对等的 vam 语法为：
```
let g:clojure:something = 0

autocmd FileType clojure :VAMActivate github:guns/vim-clojure-highlight
```

使用 YAML 格式记录插件配置，
其中 conf 部分为 配置信息，
plugins 部分为插件列表。

