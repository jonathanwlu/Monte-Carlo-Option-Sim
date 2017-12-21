import os.path as op
import pandas as pd
from plot import iv_strike_plot

if __name__ == "__main__":
    df = pd.read_csv(op.join(op.abspath(op.join(__file__, op.pardir, op.pardir, op.pardir)), 'iv_strike_input.txt'),
                     sep='=', index_col=0).dropna()
    data = df[df.columns[0]]
    args = {}
    for i in range(0, len(df.index)):
        if i in [0, 2, 5]:
            args[df.index[i]] = int(df.iloc[i, 0])
        elif i in [1, 3, 4]:
            args[df.index[i]] = float(df.iloc[i, 0])
        else:
            args[df.index[i]] = df.iloc[i, 0]

    with open(op.join(op.abspath(op.join(__file__, op.pardir, op.pardir, op.pardir)),
                      'iv_strike_input.txt'), 'r') as infile, \
         open(op.join(op.abspath(op.join(__file__, op.pardir, op.pardir, op.pardir)),
                      'out', args['filename'] + '.txt'), 'w') as outfile:
        outfile.write('INPUT\n')
        outfile.write('-' * 20 + '\n')
        outfile.write(infile.read())

    iv_strike_plot.plot(args['length'], args['start_price'], args['times'],
                        args['center_strike'], args['strike_range'], args['num_strike'],
                        filename=args['filename'], dist=args['dist'], **dict(list(data.iteritems())[8:]))
