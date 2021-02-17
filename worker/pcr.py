import json
from zzcore import StdAns
from random import randint, choice

AllowCMD = ['登记','申请出刀','报刀','挂树','查树','进度','查刀','新的一天','血量','boss','初始化','求助','迁移','踢人','单抽','十连','查看卡池','查看池子','新增角色','删除角色','设置up']

status = {
    'all_player':{
        '1318000868': {
            'id':'十六夜咲夜',
            '余刀': 3,
            '加时刀': 0,
            # 'SL':1
        },
    },
    'boss_num': 0,
    'boss_hp': 0,
    'dao':{
        'qq':1318000868,
        '类型':'普通刀',
    },
    'tree':[]
}

class Ans(StdAns):
    AllowGroup = [125733077,1084566280,920863253]
    
    def GETMSG(self):
        if len(self.parms) < 2:
            return '不加参数是坏文明！'
        
        cmd = self.parms[1]
        if cmd not in AllowCMD:
            return '没有 ' + cmd + ' 这个命令，请检查。'

        if cmd == '迁移':
            if self.uid != 1318000868:
                return '迁移数据请联系SiHuan'
            try:
                nowdata = json.loads(self.DATAGET()[self.parms[2]])
            except:
                return '获取原始数据出错!'
            self.DATASET({self.parms[3]:json.dumps(nowdata)})
            return '数据迁移完成! ' + self.parms[2] + '现在迁移到' + self.parms[3]

        gid = str(self.gid)

        try:
            nowdata = json.loads(self.DATAGET()[gid])
        except:
            if cmd == '初始化':
                nowdata = {}
            else:
                return '请管理员先初始化,初始化会将进度设置为第一周目第一个Boss,成员数据不会丢失。'

        
        if cmd == '初始化':
            if self.role not in ['owner','admin'] and self.uid != 1318000868:
                return '你没有权限执行初始化。'
            else:
                try:
                    all_player = nowdata['all_player']
                except:
                    all_player = {}

                nowdata = {}
                nowdata['all_player'] = all_player
                nowdata['boss_num'] = 1
                nowdata['boss_hp'] = -1
                nowdata['dao'] = {
                    'qq':0,
                    '类型':'普通刀',
                }
                nowdata['tree'] = []
                self.DATASET({gid:json.dumps(nowdata)})
                return '初始化完成！请使用\n /pcr 血量 xxxx \n 来设置第一周目第一个Boss的总血量。'
        
        if cmd == '登记':
            nickname = self.raw_msg['raw_message'][8:]
            if nickname:
                player = {
                    'id':nickname,
                    '余刀': 3,
                    '加时刀': 0,
                    # 'SL':1
                }

                nowdata['all_player'][str(self.uid)] = player
                self.DATASET({gid:json.dumps(nowdata)})

                return '[CQ:at,qq=' + str(self.uid) + ']' + '游戏id设置为 ' +  nickname

            else:
                return '登记失败，请使用合法的游戏id。'

        if cmd == '踢人':
            if self.role not in ['owner','admin'] and self.uid != 1318000868:
                return '你没有权限踢人。'
            else:
                tiqq = self.parms[2]
                try:
                    nowplayer = nowdata['all_player'][tiqq]
                except:
                    return '此人未登记！！！。'

                if tiqq in nowdata['tree']:
                    nowdata['tree'].remove(tiqq)
                if str(nowdata['dao']['qq']) == tiqq:
                    nowdata['dao']['qq'] = 0
                
                del nowdata['all_player'][tiqq]
                self.DATASET({gid: json.dumps(nowdata)})
                return nowplayer['id'] + '已被踢除。'

        if cmd == '血量':
            if self.role not in ['owner','admin'] and self.uid != 1318000868:
                return '你没有权限设置血量。'
            else:
                try:
                    hp = int(self.parms[2])
                except:
                    return '血量应该是整数！'

                nowdata['boss_hp'] = hp
                self.DATASET({gid:json.dumps(nowdata)})
                return '现在' + bossname(int(nowdata['boss_num'])) +'的血量被设置为' + str(hp)

        if cmd == 'boss':
            if self.role not in ['owner','admin'] and self.uid != 1318000868:
                return '你没有权限设置boss。'
            else:
                try:
                    boss = int(self.parms[2])
                except:
                    return 'boss序号应该是整数！'

                nowdata['boss_num'] = boss
                self.DATASET({gid:json.dumps(nowdata)})
                return '现在boss被设置为' + bossname(int(nowdata['boss_num']))

        if cmd == '新的一天':
            if self.role not in ['owner','admin'] and self.uid != 1318000868:
                return '你没有权限新的一天。'
            else:
                for value in nowdata['all_player'].values():
                    value['余刀'] = 3
                    value['加时刀']  = 0
                    # value['SL'] == 1
                nowdata['tree'] = []
                self.DATASET({gid:json.dumps(nowdata)})
            return '新的一天已经开始，大家各有3刀剩余了。'

        
        if cmd == '进度':
            return bossname(int(nowdata['boss_num'])) + '\n剩余血量：' + str(nowdata['boss_hp'])

        if cmd == '申请出刀':
            try:
                nowplayer = nowdata['all_player'][str(self.uid)]
            except:
                return '您未登记。'

            if self.uid in nowdata['tree']:
                return '您在树上了。'
            
            daoqq = nowdata['dao']['qq']
            if daoqq != 0 and daoqq not in nowdata['tree']:
                return nowdata['all_player'][str(daoqq)]['id'] + '正在出刀，请等待他结算或挂树.'
            elif nowplayer['余刀'] + nowplayer['加时刀'] < 1:
                return '您已无刀可出。'
            else:
                nowdata['dao']['qq'] = self.uid
                if nowplayer['加时刀'] > 0:
                    nowdata['dao']['类型'] = '加时刀'
                else:
                    nowdata['dao']['类型'] = '普通刀'

                self.DATASET({gid:json.dumps(nowdata)})
                return nowplayer['id'] + '出' + nowdata['dao']['类型'] + '讨伐' + bossname(int(nowdata['boss_num'])) + '\n剩余血量：' + str(nowdata['boss_hp'])

        
        if cmd == '报刀':
            try:
                nowplayer = nowdata['all_player'][str(self.uid)]
            except:
                return '您未登记。'
            if nowdata['dao']['qq'] != self.uid and self.uid not in nowdata['tree']:
                return '您未出刀，报个毛刀'
            try:
                jianhp = int(self.parms[2])
            except:
                return '打掉的血量应该是整数！'

            newhp = nowdata['boss_hp'] - jianhp
            # BOSS 没死
            if newhp > 0:
                nowdata['boss_hp'] = newhp
                nowdata['dao']['qq'] = 0
                if nowdata['dao']['类型'] == '加时刀':
                    nowplayer['加时刀'] = 0
                else:
                    nowplayer['余刀'] = nowplayer['余刀'] - 1

                nowdata['all_player'][str(self.uid)] = nowplayer
                if self.uid in nowdata['tree']:
                    nowdata['tree'].remove(self.uid)
                self.DATASET({gid:json.dumps(nowdata)})
                
                msg =  nowplayer['id'] + '打了' + bossname(int(nowdata['boss_num'])) + str(jianhp) + '\n剩余血量：' + str(nowdata['boss_hp'])
                if self.uid in nowdata['tree']:
                    msg = msg + '\n' + nowplayer['id'] + '自行下树'
                return msg
            #BOSS 死了
            else:
                nowdata['boss_hp'] = 0
                nowdata['boss_num'] = nowdata['boss_num'] + 1
                nowdata['dao']['qq'] = 0
                nowdata['tree'] = []
                if nowdata['dao']['类型'] == '加时刀':
                    nowplayer['加时刀'] = 0
                else:
                    nowplayer['余刀'] = nowplayer['余刀'] - 1
                    nowplayer['加时刀'] = 1
                
                nowdata['all_player'][str(self.uid)] = nowplayer
                if self.uid in nowdata['tree']:
                    nowdata['tree'].remove(self.uid)
                self.DATASET({gid:json.dumps(nowdata)})

                return nowplayer['id'] + '击杀了' + bossname(int(nowdata['boss_num'])-1) + '\n现在进入' + bossname(int(nowdata['boss_num'])) + '\n挂树的同学已经全部下树\n请使用\n /pcr 血量 xxxx \n 来设置新Boss的总血量'

            
        if cmd == '挂树':
            try:
                nowplayer = nowdata['all_player'][str(self.uid)]
            except:
                return '您未登记。'

            if self.uid in nowdata['tree']:
                return '您已经在树上了。'

            # elif nowplayer['SL'] == 1:
            elif nowdata['dao']['qq'] != self.uid:
                return '您未出刀，挂个毛树'
            else:
                nowdata['dao']['qq'] = 0
                # print(nowdata['tree'])
                # print(type(nowdata['tree']))
                nowdata['tree'].append(self.uid)
                # print(nowdata['tree'])
                # print(type(nowdata['tree']))
                self.DATASET({gid:json.dumps(nowdata)})
                return '已挂树'

        if cmd == '查树':
            on_tree_players = ''
            for p in nowdata['tree']:
                on_tree_players = on_tree_players + nowdata['all_player'][str(p)]['id'] + '\n'
            return '树上的有\n' + on_tree_players

        if cmd == '查刀':
            alldao = ''
            index = 1
            for key, value in nowdata['all_player'].items():
                alldao = alldao + str(index) + '. ' + value['id'] + ' ' + '🔪'*value['余刀'] + '🍴'*value['加时刀']
                if int(key) in nowdata['tree']:
                    alldao = alldao + ' 在🌳上\n'
                else:
                    alldao = alldao + '\n'
                index = index + 1
            return alldao

        if cmd == '求助':
            on_tree_players = ''
            for p in nowdata['tree']:
                on_tree_players = on_tree_players + nowdata['all_player'][str(p)]['id'] + '\n'
            return '救命[CQ:at,qq=3178302597][CQ:at,qq=3430357110]\n' + on_tree_players + '都在🌳上'

        path = './data/pcr/char.list'
        try:
            with open(path, 'r+', encoding='utf-8') as f:
                characters = f.readlines()
        except:
            return '好像角色名单没有加载呢。。。'
        star3 = characters[1].replace('\n','').split(' ')
        star3 = [each for each in star3 if each]
        star2 = characters[3].replace('\n', '').split(' ')
        star2 = [each for each in star2 if each]
        star1 = characters[5].replace('\n', '').split(' ')
        star1 = [each for each in star1 if each]
        up = characters[7].replace('\n', '').split(' ')
        up = [each for each in up if each]


        if cmd == '单抽' or cmd == '十连':
            times = 1 if cmd == '单抽' else 9
            resultStar = []
            resultName = []
            for each in range(times):
                code = randint(1,1000)
                if code <= 18:
                    resultStar.append(3)
                    resultName.append(choice(star3))
                elif code <= 25:
                    resultStar.append(3)
                    resultName.append(choice(up))
                elif code <= 205:
                    resultStar.append(2)
                    resultName.append(choice(star2))
                else:
                    resultStar.append(1)
                    resultName.append(choice(star1))
            if times == 9:
                code = randint(1, 1000)
                if code <= 18:
                    resultStar.append(3)
                    resultName.append(choice(star3))
                elif code <= 25:
                    resultStar.append(3)
                    resultName.append(choice(up))
                else:
                    resultStar.append(2)
                    resultName.append(choice(star2))
            stones = 0
            colors = '[CQ:at,qq={}]\n'.format(self.uid)
            for each in range(len(resultStar)):
                if resultStar[each] == 3:
                    stones = stones + 50
                    color = '彩'
                elif resultStar[each] == 2:
                    stones = stones + 10
                    color = '金'
                else:
                    stones = stones + 1
                    color = '银'
                if each == 4:colors = colors + color + '\n'
                else:colors = colors + color + '  '
            name = ''
            for each in range(len(resultName)):
                if each == 4: name = name + resultName[each] + '\n'
                else:name = name + resultName[each] + '  '
            name = name + '\n母猪石 +{} [CQ:face,id=108]'.format(stones)
            self.sendmsg(colors)
            self.sendmsg(name)
            if stones == 19:return '非酋在上，请受我一拜[CQ:face,id=0][CQ:face,id=118]'
            elif stones > 157:return '欧皇！[CQ:face,id=23]啊我酸了'

        if cmd == '查看卡池' or cmd == '查看池子':
            return '3★\n' + '、'.join(star3) + '\n2★\n' + '、'.join(star2) + '\n1★\n' + '、'.join(
                star1) + '\n★UP★\n' + '、'.join(up)

        if cmd == '新增角色':
            if self.role in ['owner','admin']:
                if len(self.parms) != 4:
                    return '请使用句式：/pcr 新增角色 3 镜华'
                try:
                    star = int(self.parms[2])
                except:
                    return '请使用句式：/pcr 新增角色 3 镜华'
                name = self.parms[3]
                if star == 3:
                    star3.append(name)
                elif star == 2:
                    star2.append(name)
                elif star == 1:
                    star1.append(name)
                else:
                    return '请输入正确的星级'
                char = '3* 2.5%\n{}\n2* 18%\n{}\n1* 79.5%\n{}\nup 0.7%\n{}'.format(' '.join(star3), ' '.join(star2),
                                                                                   ' '.join(star1), ' '.join(up))
                try:
                    with open(path, 'w+', encoding='utf-8') as f:
                        f.write(char)
                except:
                    return '好像角色名单没有加载呢。。。'
                return '添加新角色{}★ {} 成功[CQ:face,id=144][CQ:face,id=144]'.format(star, name)
            else:
                return '抱歉，您没有使用这条命令的权柄'

        if cmd == '删除角色':
            if self.role in ['owner','admin']:
                if len(self.parms) != 4:
                    return '请使用句式：/pcr 删除角色 3 镜华'
                try:
                    star = int(self.parms[2])
                except:
                    return '请使用句式：/pcr 删除角色 3 镜华'
                name = self.parms[3]
                try:
                    if star == 3:
                        star3.remove(name)
                    elif star == 2:
                        star2.remove(name)
                    elif star == 1:
                        star1.remove(name)
                    else:
                        return '请输入正确的星级'
                except:
                    return '没有找到对应的角色'
                char = '3* 2.5%\n{}\n2* 18%\n{}\n1* 79.5%\n{}\nup 0.7%\n{}'.format(' '.join(star3), ' '.join(star2),
                                                                                   ' '.join(star1), ' '.join(up))
                try:
                    with open(path, 'w+', encoding='utf-8') as f:
                        f.write(char)
                except:
                    return '好像角色名单没有加载呢。。。'
                return '删除角色{}★ {} 成功'.format(star, name)
            else:
                return '抱歉，您没有使用这条命令的权柄'

        if cmd == '设置up':
            if self.role in ['owner','admin']:
                if len(self.parms) != 3:
                    return '请使用句式：/pcr 设置up 镜华（多位角色请用中文逗号隔开）'
                name = self.parms[2]
                up = [each for each in name.split('，') if each]
                char = '3* 2.5%\n{}\n2* 18%\n{}\n1* 79.5%\n{}\nup 0.7%\n{}'.format(' '.join(star3), ' '.join(star2),
                                                                                   ' '.join(star1), ' '.join(up))
                try:
                    with open(path, 'w+', encoding='utf-8') as f:
                        f.write(char)
                except:
                    return '好像角色名单没有加载呢。。。'
                return '已成功将{}设为★UP★角色'.format(name)
            else:
                return '抱歉，您没有使用这条命令的权柄'


def bossname(num):
    zm = int(num/5)+1
    z = num%5

    if z == 0:
        z = 5
        zm = zm - 1

    return '第'+ str(zm) + '周目第' + str(z) + 'Boss'

