import numpy as np
import torch
import sample_comorbidities

"""CHINA DATA"""
n_ages = np.zeros(101)
p_diabetes_raw = sample_comorbidities.p_comorbidity('China', 'diabetes')
p_hypertension_raw = sample_comorbidities.p_comorbidity('China', 'hypertension')
p_CVD_raw = sample_comorbidities.p_comorbidity('China', 'CVD')

intervals = [(0, 9), (10, 19), (20, 29), (30, 39), (40, 49),
             (50, 59), (60, 69), (70, 79), (80, 100)]

p_age = torch.zeros(len(intervals)).double()
p_age[0] = 3619
p_age[1] = 7600
p_age[2] = 8571
p_age[3] = 10008
p_age[4] = 8583
p_age[5] = 3918
p_age[6] = 1408
p_age = p_age/p_age.sum()

# target
target_diabetes = torch.tensor(0.073).double()
target_hyp = torch.tensor(0.06).double()
target_age = torch.tensor([0.0, 0.2, 0.2, 0.2, 0.4, 1.3, 3.6, 8.0, 14.8]).double()
target_age = target_age / 100
target_CVD = torch.tensor(0.105).double()
target_CFR = torch.tensor(0.023).double()

# rebucketing. Need to estimate prevalence of comorbidities in age buckets
p_diabetes = np.zeros(len(intervals))
p_hypertension = np.zeros(len(intervals))
p_CVD = np.zeros(len(intervals))
for i in range(len(n_ages)):
    for j in range(len(intervals)):
        if intervals[j][0] <= i <= intervals[j][1]:
            p_diabetes[j] += p_diabetes_raw[i]
            p_hypertension[j] += p_hypertension_raw[i]
            p_CVD[j] += p_CVD_raw[i]
for j in range(len(intervals)):
    p_diabetes[j] = p_diabetes[j] / (intervals[j][1] - intervals[j][0] + 1)
    p_hypertension[j] = p_hypertension[j] / (intervals[j][1] - intervals[j][0] + 1)
    p_CVD[j] = p_CVD[j] / (intervals[j][1] - intervals[j][0] + 1)

p_diabetes = torch.from_numpy(p_diabetes)
p_hypertension = torch.from_numpy(p_hypertension)
p_CVD = torch.from_numpy(p_CVD)

num_restarts = 10
c_age_store = torch.zeros(num_restarts, len(intervals)).double()
c_diabetes_store = torch.zeros(num_restarts).double()
c_hyp_store = torch.zeros(num_restarts).double()
c_CVD_store = torch.zeros(num_restarts).double()

p_diabetes = p_diabetes / torch.sum(p_diabetes * p_age) * 0.053
p_hypertension = p_hypertension / torch.sum(p_hypertension * p_age) * 0.128
p_CVD = p_CVD / torch.sum(p_CVD * p_age) * 0.042

# assumptions: hypertension is independent of CVD given diabetes
p_dh = p_diabetes * (1 - 0.5)
p_dnh = p_diabetes * (1 - 0.5)
p_ndh = p_hypertension * (1 - 0.8)
p_ch = p_CVD * 0.456
p_cnh = p_CVD * (1 - 0.456)
p_cd = p_CVD * 0.135
p_cnd = p_CVD * (1 - 0.135)

p_cdh = p_CVD * 0.135 * 0.5
p_ncdh = p_dh - p_cdh
p_cndh = p_ch - p_cdh
p_cdnh = p_cd - p_cdh
p_ncndh = p_ndh - p_cndh
p_ncdnh = p_dnh - p_cdnh
p_cndnh = p_cnh - p_cdnh

p_ncndnh = 1 - p_cdh - p_ncdh - p_cndh - p_cdnh - p_ncndh - p_ncdnh - p_cndnh

"""ITALY DATA"""
eps = 0.00001
italy_target_age = torch.tensor([eps, eps, eps, 0.3, 0.6, 1.3, 5., 15.3, 23.3]).double() / 100
italy_deceased = torch.tensor([0., 0., 0., 12., 38., 138., 469., 1585., 1806.]).double()
italy_p_age = italy_deceased / italy_target_age
italy_p_age = italy_p_age / torch.sum(italy_p_age)
italy_target_deceased_hypertension = 0.738
italy_target_deceased_diabetes = 0.339

italy_p_diabetes_raw = sample_comorbidities.p_comorbidity('Italy', 'diabetes')
italy_p_hypertension_raw = sample_comorbidities.p_comorbidity('Italy', 'hypertension')
italy_p_CVD_raw = sample_comorbidities.p_comorbidity('Italy', 'CVD')

italy_p_diabetes = np.zeros(len(intervals))
italy_p_hypertension = np.zeros(len(intervals))
italy_p_CVD = np.zeros(len(intervals))
for i in range(len(n_ages)):
    for j in range(len(intervals)):
        if intervals[j][0] <= i <= intervals[j][1]:
            italy_p_diabetes[j] += italy_p_diabetes_raw[i]
            italy_p_hypertension[j] += italy_p_hypertension_raw[i]
            italy_p_CVD[j] += italy_p_CVD_raw[i]
for j in range(len(intervals)):
    italy_p_diabetes[j] = italy_p_diabetes[j] / (intervals[j][1] - intervals[j][0] + 1)
    italy_p_hypertension[j] = italy_p_hypertension[j] / (intervals[j][1] - intervals[j][0] + 1)
    italy_p_CVD[j] = italy_p_CVD[j] / (intervals[j][1] - intervals[j][0] + 1)

italy_p_diabetes = torch.from_numpy(italy_p_diabetes)
italy_p_hypertension = torch.from_numpy(italy_p_hypertension)
italy_p_CVD = torch.from_numpy(italy_p_CVD)

italy_p_dh = italy_p_diabetes * (1 - 0.5)
italy_p_dnh = italy_p_diabetes * (1 - 0.5)
italy_p_ndh = italy_p_hypertension * (1 - 0.8)
italy_p_ch = italy_p_CVD * 0.456
italy_p_cnh = italy_p_CVD * (1 - 0.456)
italy_p_cd = italy_p_CVD * 0.135
italy_p_cnd = italy_p_CVD * (1 - 0.135)

italy_p_cdh = italy_p_CVD * 0.135 * 0.5
italy_p_ncdh = italy_p_dh - italy_p_cdh
italy_p_cndh = italy_p_ch - italy_p_cdh
italy_p_cdnh = italy_p_cd - italy_p_cdh
italy_p_ncndh = italy_p_ndh - italy_p_cndh
italy_p_ncdnh = italy_p_dnh - italy_p_cdnh
italy_p_cndnh = italy_p_cnh - italy_p_cdnh

italy_p_ncndnh = 1 - italy_p_cdh - italy_p_ncdh - italy_p_cndh - italy_p_cdnh - italy_p_ncndh - italy_p_ncdnh - italy_p_cndnh

def model_age(c_age, c_hyp, c_diabetes, c_CVD, c_intercept):
    # p(death | age) for each age
    return (p_cdh * torch.sigmoid(c_age + c_CVD + c_hyp + c_diabetes + c_intercept) +
        p_ncdh * torch.sigmoid(c_age + c_diabetes + c_hyp + c_intercept) +
        p_cndh * torch.sigmoid(c_age + c_CVD + c_hyp + c_intercept) +
        p_cdnh * torch.sigmoid(c_age + c_CVD + c_diabetes + c_intercept) +
        p_ncndh * torch.sigmoid(c_age + c_hyp + c_intercept) +
        p_ncdnh * torch.sigmoid(c_age + c_diabetes + c_intercept) +
        p_cndnh *  torch.sigmoid(c_age + c_CVD + c_intercept) +
        p_ncndnh * torch.sigmoid(c_age + c_intercept))

def model_hyp(c_age, c_hyp, c_diabetes, c_CVD, c_intercept):
    # p(death and hypertension | age)
    preds_by_age = (p_cdh * torch.sigmoid(c_age + c_CVD + c_hyp + c_diabetes + c_intercept) +
        p_ncdh * torch.sigmoid(c_age + c_diabetes + c_hyp + c_intercept) +
        p_cndh * torch.sigmoid(c_age + c_CVD + c_hyp + c_intercept) +
        p_ncndh * torch.sigmoid(c_age + c_hyp + c_intercept))
    # \sum_age p(death and hypertension | age) * p(age) = p(death and hypertension)
    # \sum_age p(hypertension | age) * p(age) = p(hypertension)
    return torch.sum(preds_by_age * p_age) / torch.sum(p_hypertension * p_age)

def model_diabetes(c_age, c_hyp, c_diabetes, c_CVD, c_intercept):
    preds_by_age = (p_cdh * torch.sigmoid(c_age + c_CVD + c_hyp + c_diabetes + c_intercept) +
            p_ncdh * torch.sigmoid(c_age + c_diabetes + c_hyp + c_intercept) +
            p_cdnh * torch.sigmoid(c_age + c_CVD + c_diabetes + c_intercept) +
            p_ncdnh * torch.sigmoid(c_age + c_diabetes + c_intercept))
    return torch.sum(preds_by_age * p_age) / torch.sum(p_diabetes * p_age)

def model_CVD(c_age, c_hyp, c_diabetes, c_CVD, c_intercept):
    preds_by_age = (p_cdh * torch.sigmoid(c_age + c_CVD + c_hyp + c_diabetes + c_intercept) +
        p_cndh * torch.sigmoid(c_age + c_CVD + c_hyp + c_intercept) +
        p_cdnh * torch.sigmoid(c_age + c_CVD + c_diabetes + c_intercept) +
        p_cndnh *  torch.sigmoid(c_age + c_CVD + c_intercept)) / torch.sum(p_CVD)
    return torch.sum(preds_by_age * p_age) / torch.sum(p_CVD * p_age)

def loss(c_age, c_hyp, c_diabetes, c_CVD, c_intercept):
    preds_age = model_age(c_age, c_hyp, c_diabetes, c_CVD, c_intercept)
    overall_CFR = torch.sum(preds_age * p_age)
    preds_diabetes = model_diabetes(c_age, c_hyp, c_diabetes, c_CVD, c_intercept)
    preds_hyp = model_hyp(c_age, c_hyp, c_diabetes, c_CVD, c_intercept)
    preds_CVD = model_CVD(c_age, c_hyp, c_diabetes, c_CVD, c_intercept)
    return torch.nn.MSELoss()(preds_age, target_age) + torch.nn.MSELoss()(preds_diabetes, target_diabetes) + torch.nn.MSELoss()(preds_hyp, target_hyp) + torch.nn.MSELoss()(preds_CVD, target_CVD)

for restart in range(num_restarts):
    print(restart)
    num_iter = 10000
    c_age = torch.rand(len(intervals), requires_grad=True, dtype=torch.double)
    c_diabetes = torch.rand(1, requires_grad=True, dtype=torch.double)
    c_CVD = torch.rand(1, requires_grad=True, dtype=torch.double)
    c_hyp = torch.rand(1, requires_grad=True, dtype=torch.double)
    c_intercept = torch.tensor(0., requires_grad=False, dtype=torch.double)

    optimizer = torch.optim.Adam([c_age, c_hyp, c_diabetes, c_CVD, c_intercept], lr=1e-1)
    for t in range(num_iter):
        loss_itr = loss(c_age, c_hyp, c_diabetes, c_CVD, c_intercept)
        optimizer.zero_grad()
        loss_itr.backward()
        optimizer.step()
    print(loss_itr)
    print(model_age(c_age, c_hyp, c_diabetes, c_CVD, c_intercept),
          model_hyp(c_age, c_hyp, c_diabetes, c_CVD, c_intercept).item(),
          model_diabetes(c_age, c_hyp, c_diabetes, c_CVD, c_intercept).item(),
          model_CVD(c_age, c_hyp, c_diabetes, c_CVD, c_intercept).item())
    print(c_age, c_hyp.item(), c_diabetes.item(), c_CVD.item(), c_intercept.item())

    italy_preds_by_age = (italy_p_cdh * torch.sigmoid(c_age + c_CVD + c_hyp + c_diabetes + c_intercept) +
        italy_p_ncdh * torch.sigmoid(c_age + c_diabetes + c_hyp + c_intercept) +
        italy_p_cndh * torch.sigmoid(c_age + c_CVD + c_hyp + c_intercept) +
        italy_p_cdnh * torch.sigmoid(c_age + c_CVD + c_diabetes + c_intercept) +
        italy_p_ncndh * torch.sigmoid(c_age + c_hyp + c_intercept) +
        italy_p_ncdnh * torch.sigmoid(c_age + c_diabetes + c_intercept) +
        italy_p_cndnh * torch.sigmoid(c_age + c_CVD + c_intercept) +
        italy_p_ncndnh * torch.sigmoid(c_age + c_intercept))
    print("Italy CFR by age prediction")
    print(italy_preds_by_age)

    italy_d_by_age = (italy_p_cdh * torch.sigmoid(c_age + c_CVD + c_hyp + c_diabetes + c_intercept) +
            italy_p_ncdh * torch.sigmoid(c_age + c_diabetes + c_hyp + c_intercept) +
            italy_p_cdnh * torch.sigmoid(c_age + c_CVD + c_diabetes + c_intercept) +
            italy_p_ncdnh * torch.sigmoid(c_age + c_diabetes + c_intercept))
    italy_h_by_age = (italy_p_cdh * torch.sigmoid(c_age + c_CVD + c_hyp + c_diabetes + c_intercept) +
        italy_p_ncdh * torch.sigmoid(c_age + c_diabetes + c_hyp + c_intercept) +
        italy_p_cndh * torch.sigmoid(c_age + c_CVD + c_hyp + c_intercept) +
        italy_p_ncndh * torch.sigmoid(c_age + c_hyp + c_intercept))
    italy_total_death_frac = torch.sum(italy_preds_by_age * italy_p_age)
    print(torch.sum(italy_p_age * italy_d_by_age) / italy_total_death_frac)
    print(torch.sum(italy_p_age * italy_h_by_age) / italy_total_death_frac)


    c_age_store[restart] = c_age
    c_diabetes_store[restart] = c_diabetes
    c_hyp_store[restart] = c_hyp
    c_CVD_store[restart] = c_hyp
