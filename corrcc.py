import sys
import os
import subprocess
import shutil
from enum import StrEnum
from typing import Any

import correctionlib.schemav2 as schema
from correctionlib.highlevel import open_auto


class Variable:
    HASH_SIZE = 8

    def __init__(
        self,
        *,
        correction_name: str,
        var_type: str,
        var_name: str,
        var_min: float | int | str,
        var_max: float | int | str,
        var_values: set[str | int],
    ) -> None:
        was_string = False
        correction_hash = hash(correction_name) % (10**self.HASH_SIZE)

        match var_type:
            case "real":
                var_type = "float"
            case "string":
                var_type = f"{var_name.capitalize()}_{correction_hash}"
                was_string = True
            case "int":
                pass
            case _:
                print(
                    f"ERROR: Could not identify type {var_type} for parameter {var_name}.",
                    file=sys.stderr,
                )
                sys.exit(-1)

        if var_type == "float":
            if var_min == float("-inf"):
                var_min = "-FLT_MAX"

            if var_max == float("inf"):
                var_max = "FLT_MAX"
            if var_max == float("+inf"):
                var_max = "FLT_MAX"

        if var_type == "int":
            print("WARINING: Validation of int variables is not implemented.")

        self.name: str = var_name
        self.type: str = var_type
        self.was_string: bool = was_string
        self.min: float | int | str = var_min
        self.max: float | int | str = var_max
        self.values: set[str | int] | None = var_values if var_values else None


class Target(StrEnum):
    C = "C"
    CUDA = "CUDA"

    def fail(self) -> str:
        match self:
            case Target.C:
                return "exit(-1)"
            case Target.CUDA:
                return "assert(0)"
            case _:
                print("ERROR: Unknown target.", file=sys.stderr)
                sys.exit(-1)


class CorrectionBuilder:
    def __init__(self, *, name: str, target: Target = Target.C) -> None:
        self.name: str = name
        self.vars: dict[str, Variable] = {}
        self.target = target
        self.description: str | None = ""

    def set_target(self, target: Target) -> "CorrectionBuilder":
        self.target = target

        return self

    def set_description(self, description: str | None) -> "CorrectionBuilder":
        if description:
            self.description = description

        return self

    def add_var(
        self,
        *,
        var_type: str,
        var_name: str,
        var_min: float | int | str,
        var_max: float | int | str,
        var_values: set[str | int],
    ) -> "CorrectionBuilder":
        self.vars[var_name] = Variable(
            correction_name=self.name,
            var_type=var_type,
            var_name=var_name,
            var_min=var_min,
            var_max=var_max,
            var_values=var_values,
        )

        return self

    def add_data(self, data: Any) -> "CorrectionBuilder":
        if len(self.vars) == 0:
            print("ERROR: No variables have been added.", file=sys.stderr)
            sys.exit(-1)

        if isinstance(data, schema.Binning):
            # print(f"Binning: {data.input}")
            pass
        elif isinstance(data, schema.Category):
            # print(f"Category: {data.input}")
            pass
        else:
            # print(f"Any other model.")
            pass

        return self

    def _build_enums(self) -> str:
        enums_declaration = ""
        for v in self.vars:
            if self.vars[v].was_string:
                _values = self.vars[v].values
                if _values:
                    enums_body = ", ".join([str(v) for v in _values])
                    enums_declaration += f"""
                            typedef enum {{
                                {enums_body}
                            }} {self.vars[v].type};
                            """
        return enums_declaration

    def _argument_validation(self) -> str:
        validation = ""
        for var in self.vars:
            if not self.vars[var].was_string:
                validation += f"""
                    if ({self.vars[var].name} < {self.vars[var].min} || {self.vars[var].name} > {self.vars[var].max}) { self.target.fail() };
               """
        return validation

    def dump(self) -> str:
        enums = self._build_enums()
        args = ", ".join(
            [f"{self.vars[var].type} {self.vars[var].name}" for var in self.vars]
        )

        argument_validation = self._argument_validation()

        c_func = f"""
        #include <stdlib.h>
        #include <float.h>

        {enums}
        /*{self.description}*/
        float {self.name}({args}){{
        {argument_validation}


        return 1.;
        }}

        """
        return c_func

    def save(self, *, output_dir: str = "corrections") -> None:
        os.makedirs(output_dir, exist_ok=True)
        if shutil.which("clang-format"):
            try:
                res = subprocess.run(
                    ["clang-format"], input=self.dump(), capture_output=True, text=True
                )
                if res.returncode == 0:
                    with open(f"{output_dir}/{self.name}.h", "w") as f:
                        f.write(res.stdout)
            except subprocess.CalledProcessError as e:
                print(
                    f"ERROR: Could not run clang-format failed with error: {e}",
                    file=sys.stderr,
                )
        else:
            print(
                f"WARNING: Could not format correction file. Try to install clang-format with: python3 -m pip install --user clang-format",
            )
            with open(f"{output_dir}/{self.name}.h", "w") as f:
                f.write(self.dump())


if __name__ == "__main__":
    # corr_set = schema.CorrectionSet.parse_raw(open_auto("samples/muon_Z.json.gz"))
    corr_set = schema.CorrectionSet.parse_raw(
        open_auto(
            # "/cvmfs/cms.cern.ch/rsync/cms-nanoAOD/jsonpog-integration/POG/MUO/2023_Summer23/muon_Z.json.gz"
            "/cvmfs/cms.cern.ch/rsync/cms-nanoAOD/jsonpog-integration/POG/JME/2023_Summer23/jet_jerc.json.gz"
        )
    )
    for i, c in enumerate(corr_set.corrections):
        if i == 1:
            # if c.name == "Summer23Prompt23_RunCv4_JRV1_MC_ScaleFactor_AK4PFPuppi":
            builder = CorrectionBuilder(name=c.name).set_description(c.description)

            counts, variables = c.summary()
            # print(counts)
            # print(variables)
            print(type(c.data))
            print(dir(c.data))
            print(c.data.edges)
            print(c.data.flow)
            print(c.data.input)
            # print("c.data.content", c.data.content)
            content = c.data.content[2]
            print(content)
            print(dir(content))
            print(content.variables)
            print(content.expression)
            print(content.parse_raw)
            print("\n================")
            break

        # for i in c.inputs:
        #     builder = builder.add_var(
        #         var_type=i.type,
        #         var_name=i.name,
        #         var_min=variables[i.name].min,
        #         var_max=variables[i.name].max,
        #         var_values=variables[i.name].values,
        #     )
        #
        # builder = builder.add_data(c.data).save()

        # print(c.name)
        # print(c.inputs)
        # print(c.output)
        # counts, variables = c.summary()
        # for var in variables:
        #     print(var, variables[var].values)
        #     print(var, variables[var].transform)
        # print(c.summary())
        # print(c.inputs)
        # foo = c.json(indent=3)
        # with open("foo.json", "w") as f:
        #     f.write(foo)

    # import correctionlib
    # ceval = correctionlib.CorrectionSet.from_file(
    #     "/cvmfs/cms.cern.ch/rsync/cms-nanoAOD/jsonpog-integration/POG/JME/2023_Summer23/jet_jerc.json.gz"
    # )["Summer23Prompt23_RunCv123_V1_DATA_L1FastJet_AK4PFPuppi"]
    #
    # print(ceval.evaluate(5.0, 1.0, -3.0, 0.2))
