import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import chi2_contingency, pearsonr
from scipy import stats

# 한글 폰트 설정 (matplotlib)
plt.rcParams['font.family'] = 'Malgun Gothic'  # Windows
plt.rcParams['axes.unicode_minus'] = False

# 데이터 로드
df = pd.read_csv('titanic.csv')

print("=" * 60)
print("타이타닉 데이터 Survived 상관관계 분석")
print("=" * 60)
print(f"\n데이터 shape: {df.shape}")
print(f"\n컬럼: {df.columns.tolist()}")
print(f"\n결측치:")
print(df.isnull().sum())

# 데이터 타입 확인
print(f"\n데이터 타입:")
print(df.dtypes)

# Survived 분포 확인
print(f"\nSurvived 분포:")
print(df['Survived'].value_counts())
print(f"생존률: {df['Survived'].mean():.2%}")

# 1. 수치형 변수와의 상관관계 분석
print("\n" + "=" * 60)
print("1. 수치형 변수와 Survived의 상관관계 (Pearson)")
print("=" * 60)

numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
numeric_cols.remove('PassengerId')  # PassengerId는 제외
if 'Survived' in numeric_cols:
    numeric_cols.remove('Survived')

correlations = {}
for col in numeric_cols:
    if df[col].notna().sum() > 0:  # 결측치가 있는 경우 처리
        valid_data = df[[col, 'Survived']].dropna()
        if len(valid_data) > 0:
            corr, p_value = pearsonr(valid_data[col], valid_data['Survived'])
            correlations[col] = {'correlation': corr, 'p_value': p_value, 'abs_corr': abs(corr)}

# 상관계수 절댓값 기준으로 정렬
sorted_corr = sorted(correlations.items(), key=lambda x: x[1]['abs_corr'], reverse=True)

print("\n상관계수 (절댓값 기준 내림차순):")
print(f"{'변수':<15} {'상관계수':<15} {'절댓값':<15} {'p-value':<15}")
print("-" * 60)
for col, stats in sorted_corr:
    print(f"{col:<15} {stats['correlation']:>10.4f}   {stats['abs_corr']:>10.4f}   {stats['p_value']:>10.4e}")

# 2. 범주형 변수와의 상관관계 분석 (Cramer's V)
print("\n" + "=" * 60)
print("2. 범주형 변수와 Survived의 상관관계 (Cramer's V)")
print("=" * 60)

def cramers_v(x, y):
    """Cramer's V 통계량 계산"""
    confusion_matrix = pd.crosstab(x, y)
    chi2 = chi2_contingency(confusion_matrix)[0]
    n = confusion_matrix.sum().sum()
    min_dim = min(confusion_matrix.shape) - 1
    if min_dim == 0:
        return 0
    return np.sqrt(chi2 / (n * min_dim))

categorical_cols = ['Pclass', 'Sex', 'Embarked']
# Name, Ticket, Cabin은 제외 (너무 많은 고유값)

categorical_correlations = {}
for col in categorical_cols:
    if df[col].notna().sum() > 0:
        valid_data = df[[col, 'Survived']].dropna()
        if len(valid_data) > 0:
            # 카이제곱 검정
            contingency = pd.crosstab(valid_data[col], valid_data['Survived'])
            chi2, p_value, dof, expected = chi2_contingency(contingency)
            cramers_v_value = cramers_v(valid_data[col], valid_data['Survived'])
            categorical_correlations[col] = {
                'cramers_v': cramers_v_value,
                'chi2': chi2,
                'p_value': p_value
            }

# Cramer's V 기준으로 정렬
sorted_cat = sorted(categorical_correlations.items(), key=lambda x: x[1]['cramers_v'], reverse=True)

print("\nCramer's V (내림차순):")
print(f"{'변수':<15} {'Cramer\'s V':<15} {'Chi-square':<15} {'p-value':<15}")
print("-" * 60)
for col, stats in sorted_cat:
    print(f"{col:<15} {stats['cramers_v']:>10.4f}   {stats['chi2']:>12.2f}   {stats['p_value']:>10.4e}")

# 3. 시각화
fig = plt.figure(figsize=(20, 12))

# 3-1. 전체 상관관계 히트맵 (수치형 변수)
ax1 = plt.subplot(2, 3, 1)
numeric_df = df[numeric_cols + ['Survived']].select_dtypes(include=[np.number])
corr_matrix = numeric_df.corr()
sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm', center=0, 
            square=True, linewidths=1, cbar_kws={"shrink": 0.8}, ax=ax1)
ax1.set_title('수치형 변수 상관관계 히트맵', fontsize=14, fontweight='bold')
plt.setp(ax1.get_xticklabels(), rotation=45, ha='right')
plt.setp(ax1.get_yticklabels(), rotation=0)

# 3-2. Survived와의 상관계수 막대 그래프
ax2 = plt.subplot(2, 3, 2)
corr_with_survived = []
corr_names = []
for col, stats in sorted_corr:
    corr_with_survived.append(stats['correlation'])
    corr_names.append(col)

colors = ['red' if x < 0 else 'blue' for x in corr_with_survived]
bars = ax2.barh(corr_names, corr_with_survived, color=colors, alpha=0.7)
ax2.axvline(x=0, color='black', linestyle='-', linewidth=0.5)
ax2.set_xlabel('상관계수', fontsize=12)
ax2.set_title('Survived와 수치형 변수 상관계수', fontsize=14, fontweight='bold')
ax2.grid(axis='x', alpha=0.3)

# 값 표시
for i, (bar, val) in enumerate(zip(bars, corr_with_survived)):
    ax2.text(val + (0.02 if val >= 0 else -0.02), i, f'{val:.3f}', 
             va='center', ha='left' if val >= 0 else 'right', fontsize=9)

# 3-3. Survived와 주요 수치형 변수 박스플롯
ax3 = plt.subplot(2, 3, 3)
# 가장 상관관계가 높은 3개 변수 선택
top_3_numeric = [col for col, _ in sorted_corr[:3]]
for i, col in enumerate(top_3_numeric):
    if df[col].notna().sum() > 0:
        data_0 = df[df['Survived'] == 0][col].dropna()
        data_1 = df[df['Survived'] == 1][col].dropna()
        positions = [i*3, i*3+1]
        bp = ax3.boxplot([data_0, data_1], positions=positions, widths=0.6,
                        patch_artist=True, labels=['사망', '생존'])
        bp['boxes'][0].set_facecolor('lightcoral')
        bp['boxes'][1].set_facecolor('lightblue')
        ax3.text(i*3+0.5, ax3.get_ylim()[1]*0.95, col, 
                ha='center', fontsize=9, fontweight='bold')

ax3.set_ylabel('값', fontsize=12)
ax3.set_title('생존 여부별 주요 수치형 변수 분포', fontsize=14, fontweight='bold')
ax3.set_xticks([i*3+0.5 for i in range(len(top_3_numeric))])
ax3.set_xticklabels([col for col in top_3_numeric], rotation=45, ha='right')
ax3.legend([bp['boxes'][0], bp['boxes'][1]], ['사망', '생존'], loc='upper right')
ax3.grid(axis='y', alpha=0.3)

# 3-4. Cramér's V 막대 그래프
ax4 = plt.subplot(2, 3, 4)
cat_names = [col for col, _ in sorted_cat]
cat_values = [stats['cramers_v'] for _, stats in sorted_cat]
bars = ax4.barh(cat_names, cat_values, color='green', alpha=0.7)
ax4.set_xlabel("Cramer's V", fontsize=12)
ax4.set_title('Survived와 범주형 변수 상관관계 (Cramer\'s V)', fontsize=14, fontweight='bold')
ax4.grid(axis='x', alpha=0.3)

for bar, val in zip(bars, cat_values):
    ax4.text(val + 0.01, bar.get_y() + bar.get_height()/2, f'{val:.3f}', 
             va='center', ha='left', fontsize=10)

# 3-5. Sex와 Survived 교차표 시각화
ax5 = plt.subplot(2, 3, 5)
sex_survived = pd.crosstab(df['Sex'], df['Survived'], normalize='index') * 100
sex_survived.plot(kind='bar', ax=ax5, color=['lightcoral', 'lightblue'], width=0.7)
ax5.set_title('성별별 생존률', fontsize=14, fontweight='bold')
ax5.set_xlabel('성별', fontsize=12)
ax5.set_ylabel('비율 (%)', fontsize=12)
ax5.set_xticklabels(ax5.get_xticklabels(), rotation=0)
ax5.legend(['사망', '생존'], loc='upper right')
ax5.grid(axis='y', alpha=0.3)

# 값 표시
for container in ax5.containers:
    ax5.bar_label(container, fmt='%.1f%%', fontsize=9)

# 3-6. Pclass와 Survived 교차표 시각화
ax6 = plt.subplot(2, 3, 6)
pclass_survived = pd.crosstab(df['Pclass'], df['Survived'], normalize='index') * 100
pclass_survived.plot(kind='bar', ax=ax6, color=['lightcoral', 'lightblue'], width=0.7)
ax6.set_title('좌석등급별 생존률', fontsize=14, fontweight='bold')
ax6.set_xlabel('좌석등급', fontsize=12)
ax6.set_ylabel('비율 (%)', fontsize=12)
ax6.set_xticklabels(ax6.get_xticklabels(), rotation=0)
ax6.legend(['사망', '생존'], loc='upper right')
ax6.grid(axis='y', alpha=0.3)

# 값 표시
for container in ax6.containers:
    ax6.bar_label(container, fmt='%.1f%%', fontsize=9)

plt.tight_layout()
plt.savefig('titanic_survival_correlation_analysis.png', dpi=300, bbox_inches='tight')
print("\n" + "=" * 60)
print("시각화 완료! 'titanic_survival_correlation_analysis.png' 파일이 저장되었습니다.")
print("=" * 60)

# 4. 종합 결과 요약
print("\n" + "=" * 60)
print("종합 결과 요약")
print("=" * 60)

print("\n[수치형 변수] Survived와 가장 상관관계가 높은 변수:")
print(f"1위: {sorted_corr[0][0]} (상관계수: {sorted_corr[0][1]['correlation']:.4f})")

print("\n[범주형 변수] Survived와 가장 상관관계가 높은 변수:")
print(f"1위: {sorted_cat[0][0]} (Cramer's V: {sorted_cat[0][1]['cramers_v']:.4f})")

plt.show()

