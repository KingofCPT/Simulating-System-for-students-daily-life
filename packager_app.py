import os
import sys
import PyInstaller.__main__


def create_exe():
    # 确保所需文件存在
    required_files = ['GUI.py', 'matrix_update.xlsx', 'sun.png', 'moon.png', 'map1.jpg', 'map2.png']
    for file in required_files:
        if not os.path.exists(file):
            print(f"错误: 找不到文件 {file}")
            return

    # PyInstaller参数
    params = [
        'GUI.py',  # 主程序文件
        '--name=Campus Navigation',  # 输出文件名
        '--onefile',  # 打包成单个文件
        '--windowed',  # 无控制台窗口
        '--clean',  # 清理临时文件
        '--noconfirm',  # 覆盖输出目录

        # 添加数据文件
        '--add-data', f'matrix_update.xlsx{os.pathsep}.',
        '--add-data', f'sun.png{os.pathsep}.',
        '--add-data', f'moon.png{os.pathsep}.',
        '--add-data', f'map1.jpg{os.pathsep}.',
        '--add-data', f'map2.png{os.pathsep}.',

        # 添加必需的库
        '--hidden-import', 'pandas',
        '--hidden-import', 'numpy',
        '--hidden-import', 'tkinter',
        '--hidden-import', 'Pillow',  # 改为 Pillow
        '--hidden-import', 'matplotlib',
        '--hidden-import', 'typing',

        # 排除不需要的库

        '--exclude-module', 'PyQt5',
        '--exclude-module', 'PySide2',
        '--exclude-module', 'nltk',
        '--exclude-module', 'scipy',
        # 调试选项
        '--debug', 'all'
    ]

    # 运行PyInstaller
    print("开始打包...")
    PyInstaller.__main__.run(params)
    print("打包完成！")


if __name__ == '__main__':
    create_exe()