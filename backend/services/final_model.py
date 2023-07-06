from .modules_mock_data import TOP, MID, BOTTOM, BUY_2X, BUY_X, SELL_2X, SELL_X, N_A, BEARISH

from backend.db.base import Data
from fastapi import HTTPException, status
from backend.services.modules import caluclate_modules_result
O_X = '0X'
N_X = 'NX'
X_1 = '1X'

class FinalModel:
    def __init__(
        self,
        adjustments: str,
        result: dict,
        asset: dict,
        adjustment_id: str,
        modules: list,
    ) -> dict:
        self.result = result
        self.adjustment_id = adjustment_id
        self.asset = self.create_data_asset(asset)
        self.adjustments = adjustments
        self.modules = modules
        self.result_e_key = ("Module E TOP", "Module E MID", "Module E BOTTOM")
        self.top_names_modules = ("Module I", "Module J", "Module K", "Module L")
        self.bottom_names_modules = ("Module G", "Module H")
        self.module_e_legacy = {
            "Module E TOP": "Module M",
            "Module E MID": "Module O",
            "Module E BOTTOM": "Module N",
        }
        self.final_result = {}
        self.rules_by_position = {
            "Module E TOP": {
                0: BUY_X,
                1: N_A,
                2: SELL_X,
                "F": "1x",
                "new_position": X_1
            },
            "Module E MID": {
                0: BUY_2X,
                1: BUY_X,
                2: N_A,
                "F": "1x",
                "new_position": N_X
            },
            "Module E BOTTOM": {
                0: BUY_X,
                1: N_A,
                2: SELL_X,
                "F": "1x",
                "new_position": X_1
            },
            "Module M": {
                0: N_A,
                1: SELL_X,
                2: SELL_2X,
                "F": N_A,
                "new_position": O_X
            },
            "Module N": {
                0: N_A,
                1: SELL_X,
                2: SELL_2X,
                "F": N_A,
                "new_position": O_X
            },
            "Module O": {
                0: N_A,
                1: SELL_X,
                2: SELL_2X,
                "F": N_A,
                "new_position": O_X
            },
            "Module I": {
                0: BUY_2X,
                1: BUY_X,
                2: N_A,
                "F": "1x",
                "new_position": N_X
            },
            "Module J": {
                0: BUY_X,
                1: N_A,
                2: SELL_X,
                "F": N_A,
                "new_position": X_1
            },
            "Module K": {
                0: BUY_2X,
                1: BUY_X,
                2: N_A,
                "F": "1x",
                "new_position": N_X
            },
            "Module L": {
                0: N_A,
                1: SELL_X,
                2: SELL_2X,
                "F": N_A,
                "new_position": O_X
            },
            "Module G": {
                0: N_A,
                1: SELL_X,
                2: SELL_2X,
                "F": N_A,
                "new_position": O_X
            },
            "Module H": {
                0: BUY_2X,
                1: BUY_X,
                2: N_A,
                "F": "1x",
                "new_position": N_X
            },
            "Module D": {
                0: BUY_2X,
                1: BUY_X,
                2: N_A,
                "F": "1x",
                "new_position": N_X
            },
        }

    def create_data_asset(self, asset):
        adjustment = asset.get("adjustment_ids", {}).get(self.adjustment_id)
        if adjustment:
            close = adjustment.get("close")
            if close:
                asset["close"] = close
        return asset

    def return_bad_request(self, message):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{message} {self.stop_date}",
        )

    def get_value_by_position(self, key_name):
        position = self.asset.get("position")
        position = position if position <= 1 else 2
        current_result_P = self.final_result[key_name]
        if current_result_P != N_A:
            current_result_P = self.rules_by_position[key_name][position]
        return current_result_P

    def get_value_new_position(self, key_name):
        if self.final_result[key_name] == N_A:
            key_name = self.default_modules_name
        if self.asset.get('momentum') == BEARISH:
            return self.rules_by_position[key_name]['F']
        return self.rules_by_position[key_name]["new_position"]

    def get_asset_data(self, count: int) -> dict:
        period = self.asset["period"]
        filter_fields = {
            "date": {"$lte": self.asset["date"]},
            "type_asset": self.asset["type_asset"],
            "period": period,
        }
        asset = Data.aggregate(
            [{"$match": filter_fields}, {"$sort": {"date": -1}}, {"$limit": count}]
        )

        return asset

    def get_data_previous_period(self, count: int) -> dict:
        assets = self.get_asset_data(count)
        if not assets:
            self.return_bad_request("Dont have asset data available")

        new_assets = []
        for asset in assets:
            new_a = self.create_data_asset(asset)
            try:
                new_a["result"] = caluclate_modules_result(
                    self.modules, asset=asset, adjustments=self.adjustments
                )[self.adjustment_id]
            except Exception as e:
                print("ERROR! ", e)
                new_a["result"] = {}
            new_assets.backendend(new_a)
        return new_assets

    def check_count_run_modules_E(self) -> None:
        previous_data = self.get_data_previous_period(2)
        if previous_data:
            previous_asset = previous_data.pop()
            previous_result = previous_asset.pop("result")
            key_name = "Module E"
            module_name = self.default_modules_name
            previous_result_D  = previous_result.get("Module D")
            if previous_result_D and previous_result_D.lower() in module_name.lower():
                key_name = self.module_e_legacy[self.default_modules_name]
                module_name = key_name
            self.final_result[module_name] = self.result[key_name]

    def get_result_top_bottom(self, names_modules: str, directional: str) -> None:
        if not names_modules:
            return {}
        days_before = len(names_modules) + 1
        previous_data = self.get_data_previous_period(days_before)
        if not previous_data:
            return
        previous_result_D = previous_data.pop().get("result", {}).get("Module D", "")
        if previous_result_D != directional and previous_result_D != N_A:
            cut_names_modules = names_modules[0: - 1]
            self.get_result_top_bottom(cut_names_modules, directional)

        else:
            previous_data = previous_data[::-1]
            for index, module_name in enumerate(names_modules):
                previous_asset = previous_data[index]
                previous_result = previous_asset.pop("result")
                previous_result_D = self.module_D(previous_asset, previous_result)

                is_result_MID = previous_result_D == MID
                if index == 0 and (previous_asset["position"] == 0 or is_result_MID):
                    cut_names_modules = names_modules[0: days_before - (2 + index)]
                    self.get_result_top_bottom(cut_names_modules, directional)
                    break
                if directional in previous_result_D or is_result_MID:
                    self.final_result[module_name] = previous_result[module_name]


    def get_result_key(self) -> str:
        return list(self.final_result)[-1]

    def module_D(self, asset: dict, result: dict) -> str:
        previous_result_D = result.get("Module D")
        if previous_result_D == N_A:
            self.default_modules_name = "Module D"
            if asset["close"] > asset["trend_values"]["3"]:
                previous_result_D = f"{TOP}-{N_A}"
            elif asset["close"] < asset["trend_values"]["0"]:
                previous_result_D = f"{BOTTOM}-{N_A}"
        self.final_result["Module D"] = previous_result_D
        return previous_result_D or ""

    def module_E(self, result_D: str) -> None | str:
        if not result_D: return
        if result_D == TOP:
            self.default_modules_name = "Module E TOP"
        elif result_D == MID:
            self.default_modules_name = "Module E MID"
        elif result_D == BOTTOM:
            self.default_modules_name = "Module E BOTTOM"

        self.check_count_run_modules_E()

    def module_A_C(self) -> bool:
        # IF this module returns a N/A result then we should stop here
        first_name_modules = (f"Module {module}" for module in ("A", "B", "C"))
        if False not in (self.result.get(name) for name in first_name_modules):
            return True

    def get_result(self) -> str:
        if not self.module_A_C():
            return N_A
        if self.asset.get("position") is None:
            self.return_bad_request("Missing position in the asset for date")

        result_D = self.module_D(self.asset, self.result)

        self.module_E(result_D)

        last_module_name = self.get_result_key()
        if last_module_name not in self.module_e_legacy.values():
            if result_D not in f"{BOTTOM}-{N_A}":
                self.get_result_top_bottom(self.top_names_modules, TOP)
            elif result_D not in f"{TOP}-{N_A}":
                self.get_result_top_bottom(self.bottom_names_modules, BOTTOM)

        last_module_name = self.get_result_key()
        result = {
            "Module P": self.get_value_by_position(last_module_name),
            # "last_module_name": last_module_name,
            "New Position": self.get_value_new_position(last_module_name)
        }
        return result

