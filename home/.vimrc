" All system-wide defaults are set in $VIMRUNTIME/debian.vim and sourced by
" the call to :runtime you can find below.  If you wish to change any of those
" settings, you should do it in this file (/etc/vim/vimrc), since debian.vim
" will be overwritten everytime an upgrade of the vim packages is performed.
" It is recommended to make changes after sourcing debian.vim since it alters
" the value of the 'compatible' option.

runtime! debian.vim

set nocompatible

" Vim will load $VIMRUNTIME/defaults.vim if the user does not have a vimrc.
" This happens after /etc/vim/vimrc(.local) are loaded, so it will override
" any settings in these files.
" If you don't want that to happen, uncomment the below line to prevent
" defaults.vim from being loaded.
" let g:skip_defaults_vim = 1

" Uncomment the next line to make Vim more Vi-compatible
" NOTE: debian.vim sets 'nocompatible'.  Setting 'compatible' changes numerous
" options, so any other options should be set AFTER setting 'compatible'.
"set compatible

" Vim5 and later versions support syntax highlighting. Uncommenting the next
" line enables syntax highlighting by default.
if has("syntax")
  syntax on
end




" If using a dark background within the editing area and syntax highlighting
" turn on this option as well
set background=dark

" Uncomment the following to have Vim jump to the last position when
" reopening a file
"au BufReadPost * if line("'\"") > 1 && line("'\"") <= line("$") | exe "normal! g'\"" | endif

" Uncomment the following to have Vim load indentation rules and plugins
" according to the detected filetype.
filetype plugin indent on


" ============================================================================
" 1. 插件管理 (vim-plug)
" ============================================================================
" --- 解决回车确认 Snippet 的核心逻辑 ---

call plug#begin('~/.vim/plugged')

Plug 'neoclide/coc.nvim', {'branch': 'release'} " 智能补全
Plug 'tpope/vim-commentary'      " 快捷注释: gcc
Plug 'junegunn/fzf', { 'do': { -> fzf#install() } }
Plug 'junegunn/fzf.vim'          " 模糊搜索: :Files 或 :Ag
Plug 'morhetz/gruvbox'                          " 主题
Plug 'vim-airline/vim-airline'                  " 状态栏增强 (比原生的漂亮且信息全)
Plug 'preservim/nerdtree'                       " 文件树
Plug 'vhda/verilog_systemverilog.vim'           " Verilog/SystemVerilog 语法高亮增强
Plug 'honza/vim-snippets'
call plug#end()

" ============================================================================
" 2. 基础习惯与鼠标设置
" ============================================================================
set mouse=a             " 开启鼠标支持 (点击、滚动)
set showcmd             " 在右下角显示未完成的指令
set hidden              " 切换 buffer 时不强制保存
set backspace=indent,eol,start " 解决退格键删不掉内容的问题
set ruler               " 显示光标位置标尺
nnoremap <BS> X

" ============================================================================
" 3. UI 与显示优化
" ============================================================================
set number              " 显示绝对行号
set cursorline          " 高亮当前行
set showmatch           " 匹配括号高亮
set matchtime=2         " 括号匹配高亮时间 (0.2秒)
set termguicolors       " 开启 24 位真彩色支持
colorscheme gruvbox     " 配色方案
set background=dark     " 暗色模式
set scrolloff=8         " 翻页时上下留 8 行余量
set signcolumn=yes      " 始终显示左侧图标栏 (防止补全时屏幕抖动)

" ============================================================================
" 4. 工业级缩进与文件处理 (4空格标准)
" ============================================================================
set tabstop=4
set shiftwidth=4
set softtabstop=4
set expandtab           " Tab 转为空格
set smartindent         " 智能缩进
set noswapfile          " 禁用 swap 文件
set nobackup            " 禁用备份
set nowritebackup       " 提升保存时的稳定性
set updatetime=300      " 加快插件响应 (如报错提示)

" --- 搜索设置 ---
set hlsearch            " 高亮搜索结果
set incsearch           " 边输入边跳转
set ignorecase          " 搜索忽略大小写
set smartcase           " 只有输入大写时才敏感

" ============================================================================
" 5. 代码折叠逻辑
" ============================================================================
set foldenable          " 开启折叠
set foldmethod=indent   " 采用缩进折叠 (高效且符合 Verilog/C 逻辑)
set foldlevel=99        " 默认不收起代码
nnoremap <space> @=((foldclosed(line('.')) < 0) ? 'zc' : 'zo')<CR> " 空格开关折叠

" ============================================================================
" 6. 终极补全逻辑：Tab 智能跳转版
" ============================================================================

" --- Tab 键逻辑 (核心) ---
" 1. 菜单可见？ -> 确认选中项 (如果选中的是 Snippet，这里就会自动展开并选中 name)
" 2. 是跳转位置？ -> 执行跳转 (相当于 Ctrl+j)
" 3. 没菜单？ -> 输入 Tab
inoremap <silent><expr> <TAB>
      \ coc#pum#visible() ? coc#pum#confirm() :
      \ coc#expandableOrJumpable() ? "\<C-r>=coc#rpc#request('doKeymap', ['snippets-expand-jump',''])\<CR>" :
      \ CheckBackspace() ? "\<TAB>" :
      \ coc#refresh()

" --- Shift+Tab ---
inoremap <expr><S-TAB> coc#pum#visible() ? coc#pum#prev(1) : "\<C-h>"

" --- 回车键逻辑 ---
" 既然 Tab 负责了一切，回车就只负责普通换行，防止冲突
inoremap <silent><expr> <CR> coc#pum#visible() ? coc#pum#confirm() : "\<CR>"

" --- 跳转键定义 (Ctrl+j) ---
" 这是一个双重保险：除了 Tab，你也可以用 Ctrl+j 主动跳到下一个坑
let g:coc_snippet_next = '<c-j>'
let g:coc_snippet_prev = '<c-k>'
imap <C-j> <Plug>(coc-snippets-expand-jump)

" --- 辅助函数 ---
function! CheckBackspace() abort
  let col = col('.') - 1
  return !col || getline('.')[col - 1]  =~# '\s'
endfunction

" ============================================================================
" 7. 自动命令与快捷键
" ============================================================================
" 一键清除搜索高亮
nnoremap <silent> <leader>l :nohlsearch<CR>


nnoremap <C-_> :Commentary<CR>
vnoremap <C-_> :Commentary<CR>

" 像 VSCode 一样搜索文件名 (Ctrl + P)
nnoremap <C-p> :Files<CR>
" 像 VSCode 一样全局搜索文字内容 (Ctrl + F)
nnoremap <C-f> :Ag<CR>


" 1. 强制撤销：每输入一个词都自动建立撤销点，按下时执行 u
inoremap <C-z> <C-g>u<C-o>u
nnoremap <C-z> u

" 2. 强制重做：映射为 Ctrl-R
inoremap <C-y> <C-g>u<C-o><C-r>
nnoremap <C-y> <C-r>

" 3. 屏蔽终端挂起信号（防止系统抢夺 Ctrl-Z）
if !has('gui_running')
  nnoremap <C-z> u
  set t_u7=
endif


" F3 开启/关闭左侧文件树
nnoremap <F3> :NERDTreeToggle<CR>

" 格式化保护：只在当前目录有配置文件时才自动格式化
function! GlobalSafeFormat()
    let l:save_view = winsaveview()
    
    " C/C++ 格式化逻辑
    if &filetype == 'c' || &filetype == 'cpp'
        if executable('clang-format')
            let l:style = "{BasedOnStyle: Google, IndentWidth: 4}"
            silent exec "%!clang-format --style='" . l:style . "'"
        endif

    " Verilog/SystemVerilog 格式化逻辑
    elseif &filetype == 'verilog' || &filetype == 'systemverilog'
        if executable('verible-verilog-format')
            " 使用临时变量存储格式化后的内容
            " 即使失败，也不会直接修改当前 buffer
            let l:cmd = "verible-verilog-format --indent_width=4 --column_limit=100 -"
            let l:output = system(l:cmd, getline(1, '$'))
            
            if v:shell_error == 0
                " 只有在命令执行成功（返回码为 0）时才替换内容
                silent %delete
                call setline(1, split(l:output, "\n"))
            endif
        endif
    endif

    call winrestview(l:save_view)
endfunction

" 确保只在‘保存前’触发，不要在‘进入文件’时触发
" 如果您的文件里还有 BufReadPost 或 BufEnter 关联 GlobalSafeFormat，请务必删掉
autocmd BufWritePre *.c,*.cpp,*.h,*.hpp,*.v,*.sv call GlobalSafeFormat()


autocmd BufRead,BufNewFile *.v,*.sv,*.vh,*.svh set filetype=systemverilog
autocmd FileType systemverilog let b:coc_suggest_blacklist = ['c', 'cpp', 'objc', 'objcpp']
autocmd FileType systemverilog let b:coc_snippets_force_load = 1
autocmd FileType systemverilog let b:coc_snippet_filetypes = ['systemverilog', 'verilog']
au BufRead,BufNewFile *.v,*.sv,*.vh,*.svh set filetype=systemverilog
syntax enable

" Source a global configuration file if available
if filereadable("/etc/vim/vimrc.local")
  source /etc/vim/vimrc.local
endif

