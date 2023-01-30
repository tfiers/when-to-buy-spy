# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.10.0
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# +
# #!pip install yfinance
# -

from tfiers.nb import *

import yfinance

ticker = yfinance.Ticker("SPY")
price = ticker.history(period="5y")['Close'];

T_short = 4  # in business days
T_longg = 12
price_T_short_days_ago = price.shift(T_short)
price_T_longg_days_ago = price.shift(T_longg);

buy_short = price <= price_T_short_days_ago;
buy_longg = price <= price_T_longg_days_ago;

nans = pd.Series(np.nan, price.index)
buy_short_ = pd.concat((price[buy_short], nans[~buy_short])).sort_index()
buy_longg_ = pd.concat((price[buy_longg], nans[~buy_longg])).sort_index();


def plot(ax, date_offset):
    last_day = price.index[-1]
    t0 = last_day - pd.DateOffset(**date_offset)
    nans[t0:].asfreq('D').plot(color='black', label='', ax=ax)
    # hack to get nicely formatted xticks & labels
    # .. while not having gaps over the weekends in the price series
    # (which is what'd happen with `price.asfreq('D')`).
    price[t0:].plot(marker='.', ms=1.4, lw=0.7, label="S&P 500 closing price", color='black', ax=ax)
    buy_short_[t0:].plot(label=f"Price is lower than {T_short} business days ago",
                                     marker='.', ms=3, ax=ax)
    buy_longg_[t0:].plot(label=f"Price is lower than {T_longg} business days ago",
                                     lw=4, alpha=0.3, color='C2', solid_capstyle='round', ax=ax)
    ax.set_xlabel(None)


from datetime import datetime
my_timezone = datetime.now().astimezone().tzinfo
now = datetime.now(my_timezone)
title = f"Report generated on {now:%a %d %b %Y, at %H:%M (UTC%z)}";

# +
m = "main plot, medium duration"
l = "long duration (zoom out)"
s = "short duration (zoom in)"

durations = {
    m: dict(years=1),
    l: dict(years=5),
    s: dict(months=3),
}

fig = plt.figure(**figsize(width=800, aspect=1.5))
axes = fig.subplot_mosaic(
    [[m, s],
     [l, l]],
    gridspec_kw=dict(height_ratios=(1, 0.8), width_ratios=(1, 0.4))
)

for key, ax in axes.items():
    plot(ax, durations[key])
    if key == m:
        ax.legend()
        
fig.suptitle(title, size=8, color='grey', y=0.93, ha='left');
# -
# Remove existing figure file.

from pathlib import Path
desktop = Path.home() / "Desktop";  # For Unix & Windows
fname_suffix = " spy.png"
for f in desktop.glob(f"*{fname_suffix}"):
    f.unlink()

if buy_longg[-1]:
    fname_prefix = "💰💰BUY"
elif buy_short[-1]:
    fname_prefix = "💰buy"
else:
    fname_prefix = "don't buy"

mpl.rcParams['savefig.dpi'] *= 2
fig.savefig(desktop / (fname_prefix + fname_suffix), );
