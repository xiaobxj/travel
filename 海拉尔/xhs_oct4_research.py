"""Keep October 4 public-note captures separate from earlier research."""
from pathlib import Path
import xhs_route_research
xhs_route_research.OUT=Path(__file__).parent/'planning-20261004'/'xiaohongshu'
if __name__=='__main__':xhs_route_research.main()
