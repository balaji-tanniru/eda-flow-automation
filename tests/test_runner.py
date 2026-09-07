from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import pytest
from edaflow.config import load_config
from edaflow.runner import FlowError, find_tool, run_flow

def test_tool_not_found():
 with patch("edaflow.runner.shutil.which", return_value=None):
  with pytest.raises(FlowError): find_tool(None,["missing"],"Tool")

def _cfg(tmp_path):
 (tmp_path/"scripts").mkdir();(tmp_path/"scripts"/"synth.tcl").write_text("# test")
 src=tmp_path/"d.sv";src.write_text("module d; endmodule")
 from edaflow.config import FlowConfig
 return FlowConfig("d","d",(src,),tmp_path/"build",True,tmp_path)

def test_failure_writes_log_before_raise(tmp_path):
 cfg=_cfg(tmp_path); calls=[SimpleNamespace(stdout="Yosys 0.40",stderr="",returncode=0),SimpleNamespace(stdout="out",stderr="err",returncode=2)]
 with patch("edaflow.runner.shutil.which",side_effect=lambda x:x),patch("edaflow.runner.subprocess.run",side_effect=calls):
  with pytest.raises(FlowError): run_flow(cfg)
 assert (cfg.output_dir/"synthesis.log").read_text()=="outerr"

def test_version_regex_fallback_and_environment(tmp_path):
 cfg=_cfg(tmp_path); captured={}
 def fake_run(cmd,**kwargs):
  if "-V" in cmd:return SimpleNamespace(stdout="custom-version",stderr="",returncode=0)
  captured.update(kwargs["env"]);(cfg.output_dir/"stats.json").write_text('{"modules":{"\\\\d":{"num_cells":0,"num_wires":0,"num_wire_bits":0}}}')
  return SimpleNamespace(stdout="",stderr="",returncode=0)
 with patch("edaflow.runner.shutil.which",side_effect=lambda x:x),patch("edaflow.runner.subprocess.run",side_effect=fake_run):
  with patch("edaflow.runner.read_yosys_stats",return_value={}),patch("edaflow.runner.write_summary",side_effect=lambda p,**k:p.write_text("ok")): run_flow(cfg)
 assert {"EDA_TOP","EDA_SOURCE_MANIFEST","EDA_OUTPUT_DIR","EDA_FLATTEN","EDA_YOSYS"} <= captured.keys()

def test_second_design_config_loads():
 cfg=load_config(Path(__file__).parents[1]/"configs"/"toggle_counter.yaml")
 assert cfg.top=="toggle_counter" and cfg.sources[0].name=="toggle_counter.sv"
