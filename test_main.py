
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import main


class VirtualPetTests(unittest.TestCase):
    def setUp(self):
        self.pet = {
            "name": "Тузик",
            "hunger": 50,
            "energy": 50,
            "happiness": 50,
            "turns": 0,
        }
        self.output = StringIO()

    def test_change_stat_limits_values(self):
        """Характеристика не выходит за диапазон 0–100."""
        self.assertEqual(main.change_stat(90, 20), 100)
        self.assertEqual(main.change_stat(10, -30), 0)
        self.assertEqual(main.change_stat(50, 10), 60)

    def test_create_pet_and_empty_name(self):
        """Новый питомец получает начальные значения; пустое имя заменяется."""
        pet = main.create_pet("  Барсик  ")
        self.assertEqual(pet["name"], "Барсик")
        self.assertEqual(pet["hunger"], 50)
        self.assertEqual(pet["energy"], 50)
        self.assertEqual(pet["happiness"], 50)
        self.assertEqual(pet["turns"], 0)
        self.assertEqual(main.create_pet("   ")["name"], "Бублик")

    def test_feed_pet(self):
        """Кормление уменьшает голод и повышает счастье."""
        with redirect_stdout(self.output):
            result = main.feed_pet(self.pet)
        self.assertTrue(result)
        self.assertEqual(self.pet["hunger"], 25)
        self.assertEqual(self.pet["happiness"], 55)

    def test_feed_does_not_exceed_limits(self):
        """Кормление не выводит характеристики за пределы 0–100."""
        self.pet["hunger"] = 0
        self.pet["happiness"] = 98
        with redirect_stdout(self.output):
            main.feed_pet(self.pet)
        self.assertEqual(self.pet["hunger"], 0)
        self.assertEqual(self.pet["happiness"], 100)

    def test_play_pet(self):
        """При достаточной энергии игра повышает счастье и расходует ресурсы."""
        with redirect_stdout(self.output):
            result = main.play_with_pet(self.pet)
        self.assertTrue(result)
        self.assertEqual(self.pet["happiness"], 65)
        self.assertEqual(self.pet["energy"], 35)
        self.assertEqual(self.pet["hunger"], 60)

    def test_play_is_blocked_when_energy_is_low(self):
        """При энергии ниже 15 игра не меняет характеристики."""
        self.pet["energy"] = 14
        before = self.pet.copy()
        with redirect_stdout(self.output):
            result = main.play_with_pet(self.pet)
        self.assertFalse(result)
        self.assertEqual(self.pet, before)

    def test_sleep_restores_energy(self):
        """Сон восстанавливает энергию, но не превышает 100."""
        self.pet["energy"] = 80
        with redirect_stdout(self.output):
            result = main.let_pet_sleep(self.pet)
        self.assertTrue(result)
        self.assertEqual(self.pet["energy"], 100)
        self.assertEqual(self.pet["hunger"], 60)

    def test_advance_time(self):
        """Успешный игровой ход меняет показатели и увеличивает счётчик."""
        main.advance_time(self.pet)
        self.assertEqual(self.pet["turns"], 1)
        self.assertEqual(self.pet["hunger"], 55)
        self.assertEqual(self.pet["energy"], 47)
        self.assertEqual(self.pet["happiness"], 49)

    def test_mood(self):
        """Настроение определяется по характеристикам питомца."""
        self.assertEqual(main.get_mood(self.pet), "довольный")
        self.pet["hunger"] = 80
        self.assertEqual(main.get_mood(self.pet), "голодный")
        self.pet["hunger"] = 50
        self.pet["energy"] = 20
        self.assertEqual(main.get_mood(self.pet), "сонный")
        self.pet["energy"] = 50
        self.pet["happiness"] = 20
        self.assertEqual(main.get_mood(self.pet), "грустный")
        self.pet["happiness"] = 80
        self.assertEqual(main.get_mood(self.pet), "счастливый")

    def test_save_and_load_pet(self):
        """Сохранённый питомец загружается с теми же характеристиками."""
        with tempfile.TemporaryDirectory() as temp_dir:
            save_path = Path(temp_dir) / "save.json"
            with patch.object(main, "SAVE_FILE", save_path):
                with redirect_stdout(self.output):
                    self.assertTrue(main.save_pet(self.pet))
                loaded_pet = main.load_pet()

        self.assertEqual(loaded_pet, self.pet)

    def test_load_missing_save(self):
        """Если файла сохранения нет, загрузка возвращает None."""
        with tempfile.TemporaryDirectory() as temp_dir:
            save_path = Path(temp_dir) / "missing.json"
            with patch.object(main, "SAVE_FILE", save_path):
                self.assertIsNone(main.load_pet())

    def test_load_invalid_json(self):
        """Повреждённый JSON не приводит к аварийному завершению."""
        with tempfile.TemporaryDirectory() as temp_dir:
            save_path = Path(temp_dir) / "save.json"
            save_path.write_text("{invalid json", encoding="utf-8")
            with patch.object(main, "SAVE_FILE", save_path):
                with redirect_stdout(self.output):
                    loaded_pet = main.load_pet()
        self.assertIsNone(loaded_pet)


if __name__ == "__main__":
    unittest.main(verbosity=2)
