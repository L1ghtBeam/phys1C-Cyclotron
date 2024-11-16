from vpython import *

def cross(a: vector, b: vector) -> vector:
    return vector(
        a.y * b.z - a.z * b.y,
        a.z * b.x - a.x * b.z,
        a.x * b.y - a.y * b.x,
    )

def main() -> None:
    scene.width = 800
    scene.height = 800
    ## CONSTANTS ##
    mzofp = 1e-7    ## mu-zero-over-four-pi
    qe = 1.6e-19
    mproton = 1.7e-27
    B0 = vector(0, 0.2, 0)
    bscale = 1
    #### THIS CODE DRAWS A GRID ##
    #### AND DISPLAYS A MAGNETIC FIELD ##
    xmax = 0.4
    dx = 0.1
    yg = -0.1
    x = -xmax
    while x < xmax+dx:
        curve(pos=[vector(x,yg,-xmax), vector(x,yg,xmax)],
              color=vector(.7,.7,.7))
        x = x + dx
    z = -xmax
    while z < xmax+dx:
        curve(pos=[vector(-xmax,yg,z), vector(xmax,yg,z)],
              color=vector(.7,.7,.7))
        z = z + dx
    x = -xmax
    dx = 0.2
    while x < xmax+dx:
        z = -xmax
        while z < xmax+dx:
            arrow(pos=vector(x,yg,z),
                  axis=B0*bscale,
                  color=vector(0,.8,.8))
            z = z + dx
        x = x + dx
    #### OBJECTS AND INITIAL CONDITIONS
    particle = sphere(pos=vector(0,0.15,0.3),
                      radius=1e-2,
                      color=color.yellow,
                      make_trail=True)
    #### make trail easier to see (thicker) ##
    particle.trail_radius = particle.radius/3
    vparticle = vector(-2e6, 0, 0)
    p = mproton * vparticle
    qparticle = qe
    deltat = 5e-11
    t = 0
    ###########################################
    while True:
        rate(500)
        ## YOUR CODE GOES HERE ##
        if t < 3.34e-7:
            Fnet = qparticle * cross(vparticle, B0)
            p = p + Fnet * deltat

            vparticle = p/mproton
            particle.pos = particle.pos + vparticle * deltat

            t += deltat

main()