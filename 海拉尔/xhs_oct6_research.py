"""Read public notes for the October 6 itinerary review in a separate folder."""
from pathlib import Path
import xhs_route_research
xhs_route_research.OUT=Path(__file__).parent/'planning-20261006-review'/'xiaohongshu'
xhs_route_research.OUT.mkdir(parents=True,exist_ok=True)
if __name__=='__main__':xhs_route_research.main()
