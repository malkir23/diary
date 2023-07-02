from .modules_mock_data import TOP, MID, BOTTOM, BUY_2X, BUY_X, SELL_2X, SELL_X, N_A

from app.db.base import Data
from fastapi import HTTPException, status
from app.services.modules import caluclate_modules_result


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
            },
            "Module E MID": {
                0: BUY_2X,
                1: BUY_X,
                2: N_A,
                "F": "1x",
            },
            "Module E BOTTOM": {
                0: BUY_X,
                1: N_A,
                2: SELL_X,
                "F": "1x",
            },
            "Module M": {
                0: N_A,
                1: SELL_X,
                2: SELL_2X,
                "F": N_A,
            },
            "Module N": {
                0: N_A,
                1: SELL_X,
                2: SELL_2X,
                "F": N_A,
            },
            "Module O": {
                0: N_A,
                1: SELL_X,
                2: SELL_2X,
                "F": N_A,
            },
            "Module I": {
                0: BUY_2X,
                1: BUY_X,
                2: N_A,
                "F": "1x",
            },
            "Module J": {
                0: BUY_X,
                1: N_A,
                2: SELL_X,
                "F": N_A,
            },
            "Module K": {
                0: BUY_2X,
                1: BUY_X,
                2: N_A,
                "F": "1x",
            },
            "Module L": {
                0: N_A,
                1: SELL_X,
                2: SELL_2X,
                "F": N_A,
            },
            "Module G": {
                0: N_A,
                1: SELL_X,
                2: SELL_2X,
                "F": N_A,
            },
            "Module H": {
                0: BUY_2X,
                1: BUY_X,
                2: N_A,
                "F": "1x",
            },
            "Module D": {
                0: BUY_2X,
                1: BUY_X,
                2: N_A,
                "F": "1x",
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
        return self.rules_by_position[key_name][position]

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
            new_assets.append(new_a)
        return new_assets

    def check_count_run_modules(self, key_name: str) -> None:
        previous_data = self.get_data_previous_period(2)
        if previous_data:
            previous_asset = previous_data.pop()
            previous_result = previous_asset.pop("result")
            module_name = "Module E"
            result = previous_result.get(module_name)
            if previous_result.get(module_name):
                if previous_result.get("Module D", "").lower() in key_name.lower():
                    module_name = self.module_e_legacy[key_name]
                    key_name = module_name
            else:
                previous_asset = previous_data.pop()
                previous_result = previous_asset.pop("result")

            self.final_result[key_name] = result

    def get_result_top_bottom(self, names_modules: str, directional: str) -> None:
        if not names_modules:
            return {}
        days_before = len(names_modules) + 1
        previous_data = self.get_data_previous_period(days_before)
        if not previous_data:
            return
        previous_data_E = previous_data.pop()
        if previous_data_E.get("result", {}).get("Module D", "") != directional:
            if days_before - 2 > 0:
                cut_names_modules = names_modules[0 : days_before - 2]
                self.get_result_top_bottom(cut_names_modules, directional)
        else:
            previous_data = previous_data[::-1]
            for index, module_name in enumerate(names_modules):
                previous_asset = previous_data[index]
                previous_result = previous_asset.pop("result")
                if index == 0 and previous_asset["position"] == 0:
                    continue
                result_D = self.module_D(previous_asset, previous_result)

                if index > 0 and result_D != MID and directional not in result_D:
                    if days_before - 2 > 0:
                        cut_names_modules = names_modules[0 : days_before - 2 - index]
                        self.get_result_top_bottom(cut_names_modules, directional)
                else:
                    self.final_result[module_name] = previous_result[module_name]

    def get_result_key(self) -> str:
        return list(self.final_result)[-1]

    def module_D(self, asset: dict, result: dict) -> str:
        previous_result_D = result.get("Module D")
        result_D = previous_result_D
        if previous_result_D == N_A:
            if asset["close"] > asset["trend_values"]["3"]:
                result_D = f"{TOP}-{N_A}"
            elif asset["close"] < asset["trend_values"]["0"]:
                result_D = f"{BOTTOM}-{N_A}"
        self.final_result["Module D"] = result_D
        return result_D

    def module_E(self, result_D: str) -> None | str:
        if result_D == TOP:
            module_E_position = "Module E TOP"
        elif result_D == MID:
            module_E_position = "Module E MID"
        elif result_D == BOTTOM:
            module_E_position = "Module E BOTTOM"

        self.check_count_run_modules(module_E_position)

    def module_A_C(self) -> bool:
        # IF this module returns a N/A result then we should stop here
        first_name_modules = (f"Module {module}" for module in ("A", "B", "C"))
        if False not in (self.result.get(name) for name in first_name_modules):
            return True

    def get_result(self) -> str:
        if not self.module_A_C():
            return N_A

        result_D = self.module_D(self.asset, self.result)

        if self.asset.get("position") is None:
            self.return_bad_request("Missing position in the asset for date")

        if self.result.get("Module D") != N_A:
            self.module_E(result_D)

        last_module_name = self.get_result_key()
        if last_module_name not in self.module_e_legacy.values():
            if result_D not in f"{BOTTOM}-{N_A}":
                self.get_result_top_bottom(self.top_names_modules, TOP)
            elif result_D not in f"{TOP}-{N_A}":
                self.get_result_top_bottom(self.bottom_names_modules, BOTTOM)

        last_module_name = self.get_result_key()
        return self.get_value_by_position(last_module_name)
