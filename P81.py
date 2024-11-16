from vpython import *
from sys import argv
from argparse import ArgumentParser


## CONSTANTS ##
qe = 1.6e-19
mzofp = 1e-7    ## mu-zero-over-four-pi
mproton = 1.7e-27
bscale = 1


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument('-v', '--velocity', type=float, nargs=3, metavar=('X', 'Y', 'Z'),
                        help="initial velocity vector of the particle")
    parser.add_argument('-b', '--field', type=float, nargs=3, metavar=('X', 'Y', 'Z'),
                        help="magnetic field vector")
    parser.add_argument('-q', '--charge', type=float, help="charge of the particle")
    parser.add_argument('-c', '--cycles', type=int, help="number of cycles of the particle")

    args = parser.parse_args()

    kwargs = {}
    if args.velocity:
        kwargs['vparticle'] = vector(args.velocity[0], args.velocity[1], args.velocity[2])
    if args.field:
        kwargs['B0'] = vector(args.field[0], args.field[1], args.field[2])
    if args.charge:
        kwargs['qparticle'] = args.charge
    if args.cycles:
        kwargs['cycles'] = args.cycles

    simulate(**kwargs)


def simulate(
        vparticle: vector = vector(-2e6, 0, 0),
        B0: vector = vector(0, 0.2, 0),
        qparticle: float = qe,
        cycles: int = -1) -> None:
    scene.width = 800
    scene.height = 800

    make_grid(B0, bscale)

    #### OBJECTS AND INITIAL CONDITIONS
    particle = sphere(pos=vector(0,0.15,0.3),
                      radius=1e-2,
                      color=color.yellow,
                      make_trail=True)
    #### make trail easier to see (thicker) ##
    particle.trail_radius = particle.radius/3
    p = mproton * vparticle
    deltat = 5e-11
    t = 0

    # calculate the period to determine the time for each cycle
    # mag(cross(vparticle.norm(), B0)) calculates the amount of magnetic field which is perpendicular to the velocity
    # of the particle
    try:
        period = 2 * pi * mproton / abs(qparticle) / mag(cross(vparticle.norm(), B0))
    except ZeroDivisionError:
        # this is true if the particle will not form a circle (either charge is 0 or the magnetic field perpendicular
        # to the charge is 0)
        period = float('inf')

    # diameter setup
    diameter = curve(pos=[copy_vector(particle.pos), copy_vector(particle.pos)],
                     color=color.white)
    radius_printed = False
    ###########################################
    while True:
        rate(500)
        ## YOUR CODE GOES HERE ##
        if cycles < 1 or t < period * cycles:
            Fnet = qparticle * cross(vparticle, B0)
            p = p + Fnet * deltat

            vparticle = p/mproton
            particle.pos = particle.pos + vparticle * deltat

            # check and save diameter
            flat_pos = copy_vector(particle.pos, y=0.15)
            if (not radius_printed and distance(flat_pos, diameter.point(0)['pos']) >
                    distance(diameter.point(1)['pos'], diameter.point(0)['pos'])):
                diameter.modify(1, pos=flat_pos)

            t += deltat

        if t > period and not radius_printed:
            r = distance(diameter.point(0)['pos'], diameter.point(1)['pos'])/2
            print(f"radius = {r:.3f} m")
            radius_printed = True


def make_grid(b0: vector, bscale: float) -> None:
    #### THIS CODE DRAWS A GRID ##
    #### AND DISPLAYS A MAGNETIC FIELD ##
    xmax = 0.4
    dx = 0.1
    yg = -0.1
    x = -xmax
    while x < xmax + dx:
        curve(pos=[vector(x, yg, -xmax), vector(x, yg, xmax)],
              color=vector(.7, .7, .7))
        x = x + dx
    z = -xmax
    while z < xmax + dx:
        curve(pos=[vector(-xmax, yg, z), vector(xmax, yg, z)],
              color=vector(.7, .7, .7))
        z = z + dx
    x = -xmax
    dx = 0.2
    while x < xmax + dx:
        z = -xmax
        while z < xmax + dx:
            arrow(pos=vector(x, yg, z),
                  axis=b0 * bscale,
                  color=vector(0, .8, .8))
            z = z + dx
        x = x + dx


def cross(a: vector, b: vector) -> vector:
    return vector(
        a.y * b.z - a.z * b.y,
        a.z * b.x - a.x * b.z,
        a.x * b.y - a.y * b.x,
    )


def distance(a: vector, b: vector) -> float:
    return mag(a - b)


def copy_vector(v: vector, **kwargs) -> vector:
    return vector(kwargs.get('x') or v.x, kwargs.get('y') or v.y, kwargs.get('z') or v.z)



if __name__ == '__main__':
    main()