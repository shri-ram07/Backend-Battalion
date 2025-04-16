def calculate (n_fan , n_cooler , n_ac , n_light):
    avg_fan = 0.07
    avg_cooler = 0.20
    avg_ac = 1.2
    avg_light = 0.015

    res = (n_fan*avg_fan)+(n_cooler*avg_cooler)+(n_ac*avg_ac)+(n_light*avg_light)
    return res