from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd

# Konfiguracja Selenium
driver = webdriver.Chrome()  # Użyj odpowiedniego WebDrivera
driver.get("https://www.mimuw.edu.pl/pl/")  # URL strony głównej

# Czekamy na załadowanie strony
time.sleep(5)


# Funkcja do scrollowania w dół strony
def scroll_to_bottom():
    driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
    time.sleep(2)  # Czekamy na załadowanie nowych elementów


# Funkcja do wyciągania eventów z kalendarza
def extract_events():
    events_data = []
    calendar_days = driver.find_elements(By.CLASS_NAME, "calendar-day-content")

    for event in calendar_days:
        # Hover nad eventem
        ActionChains(driver).move_to_element(event).perform()
        time.sleep(0.5)  # Krótka przerwa na załadowanie tooltipa

        # Pobieranie szczegółów wydarzenia
        try:
            title = event.text.strip()
            url_element = event.find_element(By.TAG_NAME, "a")
            url = url_element.get_attribute("href")
            events_data.append({
                "title": title,
                "url": url
            })
        except Exception as e:
            print("Event bez szczegółów:", e)

    return events_data


# Główna pętla
all_events = []
visited_days = set()


# Funkcja do iteracji przez kalendarz w lewo/prawo
def navigate_calendar(direction):
    if direction == "left":
        arrow = driver.find_element(By.ID, "calendar-arrow-left")
    elif direction == "right":
        arrow = driver.find_element(By.ID, "calendar-arrow-right")
    else:
        raise ValueError("Direction must be 'left' or 'right'")

    while True:
        scroll_to_bottom()

        # Pobierz datę wyświetlaną w kalendarzu, aby uniknąć pętli
        current_date = driver.find_element(By.ID, "calendar-day-header").text.strip()
        if current_date in visited_days:
            break

        visited_days.add(current_date)

        # Wyciągnij wydarzenia
        events = extract_events()
        all_events.extend(events)

        # Kliknij strzałkę
        arrow.click()
        time.sleep(2)


# Iteruj w lewo i prawo przez kalendarz
navigate_calendar("left")
navigate_calendar("right")

# Zapisz wyniki do pliku
df = pd.DataFrame(all_events)
df.to_csv("events_mimuw.csv", index=False)

# Wyświetl przykładowe wydarzenia
print(df.sample(5))

# Zamknij przeglądarkę
driver.quit()
