-- 实习作业要求：至少 5 条高质量样例数据（含预设讨论话题与对应嘉宾阵容）
-- 本脚本可以直接在 SQLite 中执行，导入 5 个经典的圆桌讨论房间。
-- 满足要求：每个房间参会人数 >= 4 人（1名主持人 + 4名专家，共5人）

INSERT INTO rooms (id, topic, expert_count, status, created_at, updated_at) VALUES 
('room-mock-001', '通用人工智能 (AGI) 是否会在十年内引发人类大规模失业？', 5, 'finished', datetime('now', '-5 days'), datetime('now', '-5 days')),
('room-mock-002', '弹性婚姻制度：是否应该引入 5 年期合同制婚姻？', 5, 'finished', datetime('now', '-4 days'), datetime('now', '-4 days')),
('room-mock-003', '自动驾驶的伦理困境：出车祸时算法应该优先保护乘客还是路人？', 5, 'finished', datetime('now', '-3 days'), datetime('now', '-3 days')),
('room-mock-004', '外星文明探索：人类是否应该主动向宇宙广播地球的坐标？', 5, 'finished', datetime('now', '-2 days'), datetime('now', '-2 days')),
('room-mock-005', '脑机接口商业化：普通人是否有权通过芯片大幅提升智力？', 5, 'finished', datetime('now', '-1 days'), datetime('now', '-1 days'));

-- 样例房间 1 的专家阵容 (AGI) - 5人
INSERT INTO experts (id, room_id, name, title, stance, color, role, position, current_status, public_thought, created_at) VALUES
('exp-1-0', 'room-mock-001', '陈导', '科技观察员', '中立引导', '#ffffff', 'host', 0, 'idle', '', datetime('now')),
('exp-1-1', 'room-mock-001', '李极客', '硅谷AI研究员', '技术乐观派，认为AGI将把人类从苦役中解放出来', '#3B82F6', 'expert', 1, 'idle', '', datetime('now')),
('exp-1-2', 'room-mock-001', '王社会', '社会学教授', '悲观主义者，认为财富集中和失业潮不可避免', '#EF4444', 'expert', 2, 'idle', '', datetime('now')),
('exp-1-3', 'room-mock-001', '赵资本', '风投合伙人', '资本导向，认为AGI将创造千万级的新型工种', '#10B981', 'expert', 3, 'idle', '', datetime('now')),
('exp-1-4', 'room-mock-001', '孙哲学', '伦理学学者', '关注人类价值失落，认为工作本身是意义的来源', '#F59E0B', 'expert', 4, 'idle', '', datetime('now'));

-- 样例房间 2 的专家阵容 (弹性婚姻) - 5人
INSERT INTO experts (id, room_id, name, title, stance, color, role, position, current_status, public_thought, created_at) VALUES
('exp-2-0', 'room-mock-002', '林主持', '情感节目制作人', '中立', '#ffffff', 'host', 0, 'idle', '', datetime('now')),
('exp-2-1', 'room-mock-002', '周先锋', '青年文化独立撰稿人', '极力赞成，认为人性本不适合几十年如一日的捆绑', '#8B5CF6', 'expert', 1, 'idle', '', datetime('now')),
('exp-2-2', 'room-mock-002', '吴传统', '家庭伦理研究员', '坚决反对，认为契约化破坏了婚姻的神圣感和稳定性', '#EC4899', 'expert', 2, 'idle', '', datetime('now')),
('exp-2-3', 'room-mock-002', '陈法务', '婚姻家事律师', '务实派，认为能够有效解决财产分割和离婚难问题', '#14B8A6', 'expert', 3, 'idle', '', datetime('now')),
('exp-2-4', 'room-mock-002', '心理李', '心理咨询师', '担忧，认为长期安全感的丧失会导致社会焦虑增加', '#F43F5E', 'expert', 4, 'idle', '', datetime('now'));

-- 样例房间 3 的专家阵容 (自动驾驶) - 5人
INSERT INTO experts (id, room_id, name, title, stance, color, role, position, current_status, public_thought, created_at) VALUES
('exp-3-0', 'room-mock-003', '张车评', '资深汽车媒体人', '中立', '#ffffff', 'host', 0, 'idle', '', datetime('now')),
('exp-3-1', 'room-mock-003', '刘功利', '算法工程师', '功利主义，只看整体伤亡人数最小化', '#06B6D4', 'expert', 1, 'idle', '', datetime('now')),
('exp-3-2', 'room-mock-003', '钱律师', '知名法律界人士', '强调产权和保护，认为购买者必须优先受到保护否则产业无法落地', '#F43F5E', 'expert', 2, 'idle', '', datetime('now')),
('exp-3-3', 'room-mock-003', '吴道德', '伦理学教授', '康德主义，认为不能将任何人的生命作为计算的筹码', '#3B82F6', 'expert', 3, 'idle', '', datetime('now')),
('exp-3-4', 'room-mock-003', '赵大众', '普通驾驶员代表', '恐慌派，认为机器没有道德判断能力，不信任算法', '#EAB308', 'expert', 4, 'idle', '', datetime('now'));

-- 样例房间 4 的专家阵容 (黑暗森林) - 5人
INSERT INTO experts (id, room_id, name, title, stance, color, role, position, current_status, public_thought, created_at) VALUES
('exp-4-0', 'room-mock-004', '王天文', '天文馆馆长', '中立', '#ffffff', 'host', 0, 'idle', '', datetime('now')),
('exp-4-1', 'room-mock-004', '刘掩体', '理论物理学家', '遵循黑暗森林法则，认为主动广播形同自杀', '#64748B', 'expert', 1, 'idle', '', datetime('now')),
('exp-4-2', 'room-mock-004', '马星际', '外星文明狂热爱好者', '认为宇宙是善意的，早接触早升维', '#14B8A6', 'expert', 2, 'idle', '', datetime('now')),
('exp-4-3', 'room-mock-004', '陈防御', '战略防御专家', '悲观现实主义，主张隐藏自己，做好防御准备', '#EF4444', 'expert', 3, 'idle', '', datetime('now')),
('exp-4-4', 'room-mock-004', '郑社科', '人类学家', '认为外部危机能倒逼人类文明实现真正的内部大一统', '#8B5CF6', 'expert', 4, 'idle', '', datetime('now'));

-- 样例房间 5 的专家阵容 (脑机接口) - 5人
INSERT INTO experts (id, room_id, name, title, stance, color, role, position, current_status, public_thought, created_at) VALUES
('exp-5-0', 'room-mock-005', '孙医械', '医疗器材监管专家', '中立', '#ffffff', 'host', 0, 'idle', '', datetime('now')),
('exp-5-1', 'room-mock-005', '马神经', '神经科学界领军人', '技术狂热者，认为进化不能停滞，穷人也终将受益', '#3B82F6', 'expert', 1, 'idle', '', datetime('now')),
('exp-5-2', 'room-mock-005', '李平权', '社会平权运动发起人', '极度担忧生物学意义上的智力阶层隔离', '#F97316', 'expert', 2, 'idle', '', datetime('now')),
('exp-5-3', 'room-mock-005', '王保守', '保守派哲学家', '认为意识数字化会剥夺人类真正的灵魂和情感', '#64748B', 'expert', 3, 'idle', '', datetime('now')),
('exp-5-4', 'room-mock-005', '周赛博', '赛博朋克作家', '认为这是通向数字永生和群体蜂群思维的必经之路', '#10B981', 'expert', 4, 'idle', '', datetime('now'));
