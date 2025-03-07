import pyautogui
import keyboard
import time
from PIL import ImageGrab

# 인터파크 로그인 후 예매창 까지 왔다고 가정
# 좌석 색상을 통해서 매크로에 입력
# 윤태님의 질문으로 변수를 만들어서 좌표 설정할 수 있게함
# p.120 오토마우스 라이브러리 기능 참고
# 매크로 방식은 : https://seongjuk.tistory.com/entry/%EC%9D%B8%ED%84%B0%ED%8C%8C%ED%81%AC-%EC%B7%A8%EC%BC%93%ED%8C%85-%EB%A7%A4%ED%81%AC%EB%A1%9C
# 해당 링크 참조 

def get_region():
    print("좌석 영역 선택: 마우스를 좌측 상단에 위치시키고 'a' 키를 누르세요.")
    while True:
        if keyboard.read_key() == "a":
            top_left = pyautogui.position()
            print("좌측 상단 좌표:", top_left)
            break

    print("좌석 영역 선택: 마우스를 우측 하단에 위치시키고 'b' 키를 누르세요.")
    while True:
        if keyboard.read_key() == "b":
            bottom_right = pyautogui.position()
            print("우측 하단 좌표:", bottom_right)
            break

    return (top_left, bottom_right)

def get_floor_axis():
    print("2/3층 영역 선택: 마우스를 해당 위치에 올리고 'f' 키를 누르세요.")
    while True:
        if keyboard.read_key() == "f":
            floor_axis = pyautogui.position()
            print("2/3층 좌표:", floor_axis)
            return floor_axis

def get_time_axis():
    print("시간 선택 좌표: 마우스를 해당 위치에 올리고 't' 키를 누르세요.")
    while True:
        if keyboard.read_key() == "t":
            time_axis = pyautogui.position()
            print("시간 선택 좌표:", time_axis)
            return time_axis

def get_pay_axis():
    print("좌석 선택 완료(결제) 좌표: 마우스를 해당 위치에 올리고 'p' 키를 누르세요.")
    while True:
        if keyboard.read_key() == "p":
            pay_axis = pyautogui.position()
            print("좌석 선택 완료 좌표:", pay_axis)
            return pay_axis

def get_colors():
    colors = []
    print("좌석 등급 색상 선택: 마우스를 해당 좌표에 올리고 'a' 키를 눌러 색상을 추가하세요. (완료는 'c' 키)")
    # 화면 전체 캡처 (매번 캡처하지 않고, 단 한번 캡처 후 픽셀값 읽기)
    screen = ImageGrab.grab()
    while True:
        key = keyboard.read_key()
        if key == "a":
            pos = pyautogui.position()
            rgb = screen.getpixel((pos.x, pos.y)) if hasattr(pos, "x") else screen.getpixel((pos[0], pos[1]))
            colors.append(rgb)
            print("추가된 색상:", rgb)
            time.sleep(0.3)  # 키 중복 입력 방지용 딜레이
        elif key == "c":
            break
    return set(colors)

def click(x, y):
    pyautogui.click(x, y)

def double_click(x, y):
    pyautogui.click(x, y)
    pyautogui.click(x, y)

def press_key(key):
    pyautogui.press(key)

def same_routine(time_axis):
    # 시간 선택 좌표를 더블클릭한 후 위/아래 키 입력
    # 인터파크에서 시간을 갱신하기 위한 목적으로 필요하다고함 (블로그참고)
    double_click(time_axis[0], time_axis[1])
    press_key('up')
    time.sleep(0.5)
    press_key('down')

def search_seat(region, seat_colors, pay_axis, need_seat_cnt=2):
    delta_error = 10
    top_left, bottom_right = region
    screen = ImageGrab.grab()
    
    # 좌석 영역을 7픽셀 간격으로 탐색
    for y in range(top_left.y, bottom_right.y, 7):
        for x in range(top_left.x, bottom_right.x, 7):
            rgb = screen.getpixel((x, y))
            for color in seat_colors:
                if (abs(rgb[0] - color[0]) <= delta_error and
                    abs(rgb[1] - color[1]) <= delta_error and
                    abs(rgb[2] - color[2]) <= delta_error):
                    
                    if need_seat_cnt == 2:
                        rgb2 = screen.getpixel((x + 10, y))
                        for color2 in seat_colors:
                            if (abs(rgb2[0] - color2[0]) <= delta_error and
                                abs(rgb2[1] - color2[1]) <= delta_error and
                                abs(rgb2[2] - color2[2]) <= delta_error):
                                click(x, y)
                                click(x + 10, y)
                                click(pay_axis.x, pay_axis.y)
                                print("좌석 선택 완료")
                                return True
                    elif need_seat_cnt == 1:
                        click(x, y)
                        click(pay_axis.x, pay_axis.y)
                        print("좌석 선택 완료")
                        return True
    return False

def macro_loop(region, time_axis, pay_axis, seat_colors, floor_axis=None, second_floor=False, need_seat_cnt=2):
    print("매크로 실행 시작...")
    while True:
        try:
            print("동작 수행 중...")
            same_routine(time_axis)
            time.sleep(2)
            if second_floor and floor_axis:
                click(floor_axis.x, floor_axis.y)
                time.sleep(1)
            if search_seat(region, seat_colors, pay_axis, need_seat_cnt):
                break  # 좌석 선택 성공 시 루프 종료
        except Exception as e:
            print("에러 발생:", e)
            break
    print("매크로 종료.")

def main():
    print("인터파크 예매 매크로 실행 (로그인 및 예매 페이지 진입 완료 상태)")
    
    # 좌표 및 색상 설정
    region = get_region()
    mode = input("1층 매크로이면 1, 2/3층 매크로이면 2 입력: ").strip()
    floor_axis = get_floor_axis() if mode == "2" else None
    time_axis = get_time_axis()
    pay_axis = get_pay_axis()
    seat_colors = get_colors()
    
    need_seat_cnt = 1  # 연석 선택 시 2, 단일 좌석이면 1 (필요에 따라 수정)
    second_floor = True if mode == "2" else False

    print("설정 완료. 매크로를 실행합니다.")
    macro_loop(region, time_axis, pay_axis, seat_colors, floor_axis, second_floor, need_seat_cnt)

if __name__ == "__main__":
    main()
