from argparse import ArgumentParser

from vpython import *

## CONSTANTS ##
qe = 1.6022e-19
mzofp = 1e-7    ## mu-zero-over-four-pi
mproton = 1.7e-27
bscale = 0.02
escale = 3e-9


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument('-f', '--freq', type=float, metavar='MULTIPLE',
                        help="multiple of the angular frequency")
    parser.add_argument('-t', '--time', type=float, metavar='TIME',
                        help="change in time per second")
    parser.add_argument('-r', '--rate', type=int, metavar='RATE',
                        help="simulations per second")
    args = parser.parse_args()

    kwargs = {}
    if args.freq:
        kwargs['angular_freq_mult'] = args.freq
    if args.time:
        kwargs['time_per_sec'] = args.time
    if args.rate:
        kwargs['rate_val'] = args.rate

    simulate(**kwargs)


def simulate(angular_freq_mult: float = 1, time_per_sec: float=1.25e-8, rate_val: int=250) -> None:
    scene.width = 800
    scene.height = 800
    scene.align = 'left'

    B0 = vector(0, 1, 0)
    r = 0.05
    gap = 0.005
    height = 0.02

    make_grid(B0, bscale, r)
    neg, pos, field_vectors = make_cyclotron(r, gap, height)

    #### OBJECTS AND INITIAL CONDITIONS
    vparticle = vec(0, 0, 0)
    qparticle = qe

    particle = sphere(pos=vector(0, height/4, 0),
                      radius=1e-3,
                      color=color.yellow,
                      make_trail=True)
    #### make trail easier to see (thicker) ##
    particle.trail_radius = particle.radius / 3
    p = mproton * vparticle

    E = charge_shell(5000, pos, neg, field_vectors)

    # graphs
    ke_graph = graph(title="Kinetic Energy vs Time", xtitle="Time (ns)", ytitle="KE (eV)", xmin=0, ymin=0,
                     width=560, height=420, align='left')
    gc = gcurve(color=color.blue)

    # Time variables
    angular_freq = angular_freq_mult * abs(qparticle) * mag(cross(vec(1, 0, 0), B0)) / mproton
    period = 2*pi/angular_freq

    # default = 5e-11
    deltat = time_per_sec / rate_val
    print(f"Using delta_t = {deltat*1e9:.2g} ns")
    t = 0
    time_since_flip = period/4

    print(f"Frequency = {angular_freq / (2 * pi * 1e6):.3g} MHz")

    escaped_cyclotron = False
    while True:
        rate(rate_val)

        gc.plot(t*1e9, mproton*mag(vparticle)**2/2/qe)

        Fnet = vec(0, 0, 0)
        # magnetic field
        if sqrt(particle.pos.x**2 + particle.pos.z**2) <= r:
            Fnet += qparticle * cross(vparticle, B0)
        elif not escaped_cyclotron:
            escaped_cyclotron = True
            print_result(t, period, mag(vparticle))
        # electric field
        if -gap/2 <= particle.pos.x <= gap/2 and 0 <= particle.pos.y <= height and -r <= particle.pos.z <= r:
            Fnet += qparticle * E

        # momentum
        p = p + Fnet * deltat

        # motion
        vparticle = p / mproton
        particle.pos = particle.pos + vparticle * deltat

        if time_since_flip > period / 2:
            pos, neg = neg, pos
            E = charge_shell(5000, pos, neg, field_vectors)
            time_since_flip = 0

        t += deltat
        time_since_flip += deltat


def print_result(time: float, period: float, speed: float) -> None:
    print("\nParticle stats at escape:"
          f"\n  Time:  {time*1e9: >9.3g} ns"
          f"\n  Energy:{mproton * speed * speed / 2 / qe: >9.3g} eV"
          f"\n  Cycles:{time/period: >9.0f}"
          f"\n  Speed: {speed: >9.3g} m/s")


def charge_shell(voltage: float, pos: compound, neg: compound, field_vectors: [arrow]) -> vector:
    pos.color = color.red
    neg.color = color.white

    d_vec = neg.pos - pos.pos
    distance = mag(d_vec)
    direction = norm(d_vec)

    E = (voltage / distance) * direction

    for vector_arrow in field_vectors:
        vector_arrow.axis = E * escale

    return E


def make_cyclotron(r: float, gap: float, height: float) -> (compound, compound, [arrow]):
    thickness = 0.001

    cr = shapes.circle(radius=r, np=128, angle1=0, angle2=pi)
    arc = shapes.arc(radius=r, np=128, angle1=0, angle2=pi, thickness=thickness)

    floor_path = [vec(0, -thickness,0), vec(0, 0, 0)]
    wall_path = [vec(0, 0, 0), vec(0, height, 0)]
    ceiling_path = [vec(0, height, 0), vec(0, height+thickness, 0)]

    parts = [
        extrusion(shape=cr, path=floor_path),
        extrusion(shape=arc, path=wall_path),
        extrusion(shape=cr, path=ceiling_path)
    ]

    r_shell = compound(parts, origin=vec(0, 0, 0), pos=vec(gap/2, 0, 0), opacity=0.3)
    l_shell = r_shell.clone(pos=vec(-gap/2, 0, 0), axis=vec(-1, 0, 0))

    # field = box(pos=vec(0, height/2, 0), length=gap, width=r*2, height=height+2*thickness, color=color.orange,
    #             opacity=0.2)
    field_vectors = []
    x_density = 2
    y_density = 3
    z_density = 10

    dx = gap/(x_density-1)
    dy = height/(y_density-1)
    dz = 2*(r-thickness)/(z_density-1)

    x = -gap/2
    y = 0
    z = -r+thickness

    for i in range(x_density):
        for j in range(y_density):
            for k in range(z_density):
                field_vectors.append(arrow(pos=vec(x+i*dx, y+j*dy, z+k*dz), axis=vec(0.0015, 0, 0),
                                           color=color.orange))

    return r_shell, l_shell, field_vectors


def make_grid(b0: vector, bscale: float, r: float) -> None:
    #### THIS CODE DRAWS A GRID ##
    #### AND DISPLAYS A MAGNETIC FIELD ##
    xmax = 0.05
    dx = 0.01
    yg = -0.025
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
    dx = 0.01
    while x < xmax + dx:
        z = -xmax
        while z < xmax + dx:
            if sqrt(x**2 + z**2) >= r:
                z = z + dx
                continue
            arrow(pos=vector(x, yg, z),
                  axis=b0 * bscale,
                  color=vector(0, .8, .8))
            z = z + dx
        x = x + dx



if __name__ == '__main__':
    main()