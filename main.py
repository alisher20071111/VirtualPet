import json
from pathlib import Path


# Файл сохранения будет находиться рядом с main.py.
SAVE_FILE = Path(__file__).resolve().parent / "save.json"


# Ограничивает характеристику диапазоном от 0 до 100.
def change_stat(current, amount):
    return max(0, min(100, current + amount))


# Создаёт нового питомца с начальными характеристиками.
def create_pet(name):
    name = name.strip() or "Бублик"
    return {
        "name": name,
        "hunger": 50,
        "energy": 50,
        "happiness": 50,
        "turns": 0,
    }


# Определяет настроение по текущим характеристикам питомца.
def get_mood(pet):
    if pet["hunger"] >= 80:
        return "голодный"
    if pet["energy"] <= 20:
        return "сонный"
    if pet["happiness"] <= 20:
        return "грустный"
    if pet["happiness"] >= 80:
        return "счастливый"
    return "довольный"


# Показывает пользователю имя, характеристики и настроение питомца.
def show_status(pet):
    print("\n========== МОЙ ПИТОМЕЦ ==========")
    print(f"Имя: {pet['name']}")
    print(f"Голод: {pet['hunger']}/100")
    print(f"Энергия: {pet['energy']}/100")
    print(f"Счастье: {pet['happiness']}/100")
    print(f"Настроение: {get_mood(pet)}")
    print(f"Игровых ходов: {pet['turns']}")
    print("=================================\n")


# Кормит питомца. Возвращает True, если действие выполнено.
def feed_pet(pet):
    pet["hunger"] = change_stat(pet["hunger"], -25)
    pet["happiness"] = change_stat(pet["happiness"], 5)
    print(f"{pet['name']} вкусно покушал!")
    return True


# Играет с питомцем, если у него достаточно энергии.
def play_with_pet(pet):
    if pet["energy"] < 15:
        print(f"{pet['name']} слишком устал. Дай ему поспать!")
        return False

    pet["happiness"] = change_stat(pet["happiness"], 15)
    pet["energy"] = change_stat(pet["energy"], -15)
    pet["hunger"] = change_stat(pet["hunger"], 10)
    print(f"{pet['name']} весело поиграл!")
    return True


# Восстанавливает энергию питомца во время сна.
def let_pet_sleep(pet):
    pet["energy"] = change_stat(pet["energy"], 30)
    pet["hunger"] = change_stat(pet["hunger"], 10)
    print(f"{pet['name']} поспал и восстановил энергию!")
    return True


# Продвигает игровое время после успешного действия.
def advance_time(pet):
    pet["turns"] += 1
    pet["hunger"] = change_stat(pet["hunger"], 5)
    pet["energy"] = change_stat(pet["energy"], -3)
    pet["happiness"] = change_stat(pet["happiness"], -1)


# Сохраняет состояние питомца в JSON-файл.
def save_pet(pet):
    try:
        with SAVE_FILE.open("w", encoding="utf-8") as file:
            json.dump(pet, file, ensure_ascii=False, indent=4)
        print(f"Игра сохранена в файл {SAVE_FILE.name}.")
        return True
    except OSError as error:
        print(f"Не удалось сохранить игру: {error}")
        return False


# Загружает сохранение и проверяет его содержимое.
def load_pet():
    if not SAVE_FILE.exists():
        return None

    try:
        with SAVE_FILE.open("r", encoding="utf-8") as file:
            pet = json.load(file)

        # Проверяем наличие всех характеристик и корректность их типов.
        required_keys = ("name", "hunger", "energy", "happiness")
        if not isinstance(pet, dict) or not all(key in pet for key in required_keys):
            return None

        if not isinstance(pet["name"], str):
            return None

        for key in ("hunger", "energy", "happiness"):
            if isinstance(pet[key], bool) or not isinstance(pet[key], int):
                return None
            pet[key] = change_stat(pet[key], 0)

        turns = pet.get("turns", 0)
        if isinstance(turns, bool) or not isinstance(turns, int) or turns < 0:
            turns = 0
        pet["turns"] = turns
        pet["name"] = pet["name"].strip() or "Бублик"
        return pet

    except (OSError, json.JSONDecodeError):
        print("Сохранение не удалось прочитать. Будет создан новый питомец.")
        return None


# Главная функция: создаёт или загружает питомца и управляет меню.
def main():
    print("Добро пожаловать в Virtual Pet!")

    pet = load_pet()
    if pet is not None:
        answer = input(f"Найден питомец {pet['name']}. Загрузить сохранение? (д/н): ").strip().lower()
        if answer not in ("д", "да", "y", "yes"):
            name = input("Как назовём нового питомца? ")
            pet = create_pet(name)
    else:
        name = input("Как назовём питомца? ")
        pet = create_pet(name)

    print(f"\nТеперь ты заботишься о питомце {pet['name']}!")

    while True:
        print("\nЧто хочешь сделать?")
        print("1. Покормить")
        print("2. Поиграть")
        print("3. Уложить спать")
        print("4. Посмотреть состояние")
        print("5. Сохранить игру")
        print("6. Выйти из игры")

        choice = input("Выбери действие: ").strip()

        # Игровое время проходит только после успешного ухода за питомцем.
        action_completed = False

        if choice == "1":
            action_completed = feed_pet(pet)
        elif choice == "2":
            action_completed = play_with_pet(pet)
        elif choice == "3":
            action_completed = let_pet_sleep(pet)
        elif choice == "4":
            show_status(pet)
        elif choice == "5":
            save_pet(pet)
        elif choice == "6":
            save_pet(pet)
            print(f"До свидания! Береги {pet['name']}!")
            break
        else:
            print("Неизвестная команда. Выбери число от 1 до 6.")

        if action_completed:
            advance_time(pet)
            print("Прошёл один игровой ход.")


# Запускает игру только при непосредственном запуске этого файла.
if __name__ == "__main__":
    main()
