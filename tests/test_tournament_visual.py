"""Visual test for tournament mode - enable secret_mode_omega in config."""

from config import config

config.secret_mode_omega = True
config.debug_mode = True

from main import main

if __name__ == '__main__':
    print('Starting tournament mode test...')
    print('Instructions:')
    print('1. Enter 2-8 player names (press ENTER after each)')
    print('2. Press SPACE to start tournament')
    print('3. Press ENTER to start each match')
    print('4. Play matches with arrow keys (P1) and WASD (P2)')
    print('5. Watch the celebration screens!')
    print()
    main()
